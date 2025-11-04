# collective.catalogtrace

Log details about ZCatalog query performance

## Features

Logs details about each ZCatalog query:

- Query parameters
- Where the query was called
- Detailed execution:
  - Index name
  - Elapsed time
  - Count of persistent objects loaded
  - Count of new objects tracked by the Python GC

This information can be used to troubleshoot poor query performance.

There is some overhead to recording these measures.

Tracing is enabled for all queries if the TRACE_CATALOG_QUERIES environment variable is set.

Tracing can be enabled for specific requests by setting the catalogtrace cookie.

## Example Output

```
2025-11-04 09:39:39,984 INFO    [collective.catalogtrace:111][waitress-2] Catalog query completed in 0.0570s
    Query parameters:
      { 'allowedRolesAndUsers': [ 'Anonymous',
                                  'Authenticated',
                                  'Manager',
                                  'user:admin'],
        'exclude_from_nav': False,
        'is_default_page': False,
        'path': {'depth': 1, 'query': '/Plone/de'},
        'portal_type': [ 'Document',
                         'Folder',
                         'Link' ],
        'sort_on': 'getObjPositionInParent',
        'sort_order': 'ascending'}
    Query from:
      File "/Users/davisagli/Work/dlr-internet/backend/.venv/lib/python3.12/site-packages/plone/volto/browser/navigation.py", line 84, in topLevelTabs
        rawresult = catalog.searchResults(query)
      File "/Users/davisagli/Work/dlr-internet/backend/.venv/lib/python3.12/site-packages/collective/solr/monkey.py", line 19, in searchResults
        return adapter(REQUEST, **kw)
      File "/Users/davisagli/Work/dlr-internet/backend/.venv/lib/python3.12/site-packages/collective/solr/dispatcher.py", line 40, in __call__
        return self.context._cs_old_searchResults(request, **keywords)
    Details:
      Step: path | Time: 0.0098s | Results: 89 | DB Objects: +0 | GC Objects: +7
      Step: is_default_page | Time: 0.0082s | Results: 89 | DB Objects: +0 | GC Objects: +14
      Step: portal_type | Time: 0.0085s | Results: 21 | DB Objects: +0 | GC Objects: +17
      Step: exclude_from_nav | Time: 0.0102s | Results: 6 | DB Objects: +0 | GC Objects: +7
      Step: allowedRolesAndUsers | Time: 0.0102s | Results: 6 | DB Objects: +0 | GC Objects: +6
      Step: sort_on#getObjPositionInParent#asc | Time: 0.0100s | Results: 6 | DB Objects: +0 | GC Objects: +17
```

## Installation

Install collective.catalogtrace with `pip`:

```shell
pip install collective.catalogtrace
```

And to create the Plone site:

```shell
make create-site
```

## Contribute

- [Issue tracker](https://github.com/collective/collective.catalogtrace/issues)
- [Source code](https://github.com/collective/collective.catalogtrace/)

### Prerequisites ✅

- An [operating system](https://6.docs.plone.org/install/create-project-cookieplone.html#prerequisites-for-installation) that runs all the requirements mentioned.
- [uv](https://6.docs.plone.org/install/create-project-cookieplone.html#uv)
- [Make](https://6.docs.plone.org/install/create-project-cookieplone.html#make)
- [Git](https://6.docs.plone.org/install/create-project-cookieplone.html#git)
- [Docker](https://docs.docker.com/get-started/get-docker/) (optional)

### Installation 🔧

1.  Clone this repository, then change your working directory.

    ```shell
    git clone git@github.com:collective/collective.catalogtrace.git
    cd collective.catalogtrace
    ```

2.  Install this code base.

    ```shell
    make install
    ```

## License

The project is licensed under GPLv2.

## Credits and acknowledgements 🙏

Generated using [Cookieplone (0.9.10)](https://github.com/plone/cookieplone) and [cookieplone-templates (888ff69)](https://github.com/plone/cookieplone-templates/commit/888ff6948a43d8b962f4900ba1770f876e2f0243) on 2025-11-03 14:45:41.122916. A special thanks to all contributors and supporters!
