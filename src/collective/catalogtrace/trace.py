from zope.globalrequest import getRequest

import gc
import logging
import os
import pprint
import sys
import textwrap
import time
import traceback


TRACE_ALL_CATALOG_QUERIES = bool(os.environ.get("TRACE_CATALOG_QUERIES"))

logger = logging.getLogger("collective.catalogtrace")


def get_caller_info(skip=1):
    """Get formatted call stack, skipping framework levels."""
    stack = []
    skipped = True
    n = 0
    for frame in traceback.extract_stack()[::-1]:
        if "catalogtrace" in frame.filename or "ZCatalog" in frame.filename:
            continue
        if not skipped:
            stack.append(
                f'      File "{frame.filename}", line {frame.lineno}, in {frame.name}'
                + (f"\n        {frame.line}" if frame.line else "")
            )
            n += 1
        if "searchresults" in frame.name.lower():
            skipped = False
        if n == 3:
            break
    return "\n".join(reversed(stack))


class QueryStepResult:
    """A result from one step of a catalog query."""

    def __init__(
        self,
        step_name,
        start_time,
        end_time,
        result_size=None,
        persistent_load=None,
        gc_objects=None,
    ):
        self.step_name = step_name
        self.start_time = start_time
        self.end_time = end_time
        self.result_size = result_size
        self.persistent_load = persistent_load
        self.gc_objects = gc_objects

    def __str__(self):
        parts = [
            f"Step: {self.step_name}",
            f"Time: {self.end_time - self.start_time:.4f}s",
        ]
        if self.result_size is not None:
            parts.append(f"Results: {self.result_size}")
        if self.persistent_load is not None:
            parts.append(f"DB Objects: {self.persistent_load:+d}")
        if self.gc_objects is not None:
            parts.append(f"GC Objects: {self.gc_objects:+d}")
        return " | ".join(parts)


class QueryTracer:
    """Traces execution of catalog queries."""

    def __init__(self, catalog, query=None):
        self._conn = catalog._p_jar
        self._results = []
        self._start_time = self._split_time = time.perf_counter()
        self._query = pprint.pformat(query, indent=2)
        # Track initial state
        self._last_db_objects = self._count_db_objects()
        self._last_gc_objects = len(gc.get_objects())

    def _count_db_objects(self):
        """Count objects in ZODB connection cache."""
        return len(self._conn._cache)

    def add_step(self, step_name, result=None):
        """Record metrics for a query step."""
        now = time.perf_counter()
        db_objects = self._count_db_objects()
        gc_objects = len(gc.get_objects())

        r = QueryStepResult(
            step_name,
            start_time=self._split_time,
            end_time=now,
            result_size=len(result) if result is not None else None,
            persistent_load=db_objects - self._last_db_objects,
            gc_objects=gc_objects - self._last_gc_objects,
        )
        self._split_time = now
        self._results.append(r)

        # Update state for next measurement
        self._last_db_objects = db_objects
        self._last_gc_objects = gc_objects
        return r

    def log_results(self):
        """Get all recorded steps."""
        steps_text = "      " + "\n      ".join(str(step) for step in self._results)
        logger.info(
            f"Catalog query completed in {self._split_time - self._start_time:.4f}s\n"
            f"    Query parameters:\n{textwrap.indent(self._query, '      ')}\n"
            f"    Query from:\n{get_caller_info()}\n"
            f"    Details:\n{steps_text}\n"
        )
        return self._results


class DisabledQueryTracer:
    """A no-op query tracer."""

    def add_step(self, step_name, result=None):
        return

    def log_results(self):
        return


def get_tracer(catalog, query):
    request = getRequest()
    if TRACE_ALL_CATALOG_QUERIES or (
        request is not None and request.cookies.get("catalogtrace")
    ):
        return QueryTracer(catalog, query)
    return DisabledQueryTracer()


def patch_ZCatalog():
    """Patch ZCatalog CatalogPlan to include query tracing."""
    import Products.ZCatalog.Catalog

    class TracingCatalogPlan(Products.ZCatalog.plan.CatalogPlan):
        """CatalogPlan with instrumentation to call QueryTracer."""

        def __init__(self, catalog, query=None, threshold=0.1):
            super().__init__(catalog, query=query, threshold=threshold)
            self._tracer = get_tracer(catalog, query)

        def stop_split(self, name, result=None, limit=False):
            if not name.endswith("#intersection"):
                rs = sys._getframe(1).f_locals.get("rs", None)
                self._tracer.add_step(name, rs)
            return super().stop_split(name, result=result, limit=limit)

        def stop(self):
            super().stop()
            self._tracer.log_results()

    Products.ZCatalog.Catalog.CatalogPlan = TracingCatalogPlan
    logger.info("Patched ZCatalog CatalogPlan for query tracing.")
