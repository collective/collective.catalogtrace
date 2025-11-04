"""Init and utils."""

__version__ = "1.0.1"

PACKAGE_NAME = "collective.catalogtrace"

from .trace import patch_ZCatalog
patch_ZCatalog()
