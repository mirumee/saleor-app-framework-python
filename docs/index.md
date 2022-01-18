# Welcome to Saleor App Framework 

You are reading the Saleor App Framework (Python) documentation. This document should help you to quickly bootstrap a 3rd Party Saleor App, read more about those [:saleor-saleor: Saleor's documentation](https://docs.saleor.io/docs/3.0/developer/extending/apps/key-concepts){ target=_blank }.

The only supported web framework is **FastAPI**.

## Quickstart

### Install the framework

Using Poetry (recommended, [:material-file-link: installing poetry](https://python-poetry.org/docs/#installation){ target=_blank }):

```bash
poetry add git+https://github.com/saleor/saleor-app-framework-python.git@main
# (1)
```

1. Not on PyPi yet, you must install from git
   
Using Pip:

```bash
pip install git+https://github.com/saleor/saleor-app-framework-python.git@main 
```

### Create the Saleor app

To run your Saleor App you can use the ```#!python SaleorApp``` class which overloads the usual ```#!python FastAPI``` class.

```python linenums="1"
{!./docs/../samples/simple_app/app.py[ln:9]!}

{!./docs/../samples/simple_app/app.py[ln:77]!}
    # more arguments to come
)
```

You can use the ```#!python app``` instance as you would normally use the standard one, i.e. to initialize Sentry or add Middleware. None of the core FastAPI logic is changed by the framework.

#### Manifest

As described in [:saleor-saleor: App manifest](https://docs.saleor.io/docs/3.0/developer/extending/apps/manifest){ target=_blank } an app needs a manifest, the framework provides a Pydantic representation of that which needs to be provided when initializing the app.

```python linenums="1" hl_lines="2-3 6-18 22"
{!./docs/../samples/simple_app/app.py[ln:9]!}
{!./docs/../samples/simple_app/app.py[ln:17]!}
{!./docs/../samples/simple_app/app.py[ln:18]!}


{!./docs/../samples/simple_app/app.py[ln:62-74]!}


{!./docs/../samples/simple_app/app.py[ln:77-78]!}
    # more arguments to come
)
```

??? info "LazyUrl"

    ```#!python saleor_app.schemas.utils.LazyUrl``` is a lazy loader for app url paths, when a manifest is requested the app will resolve the path name to a full url of that endpoint.

#### Validate Domain

3rd Patry Apps work in a multi-tenant fashion - one app service can serve multiple Saleor instances. To prevent any Saleor instance from using your app the app need to authorize a Saleor instance that's done by a simple function that can be as simple as comparing the incoming Saleor domain or as complex to check the allowed domains in a database.

```python linenums="1" hl_lines="2 7-8 28"
{!./docs/../samples/simple_app/app.py[ln:9]!}
from saleor_app.schemas.core import DomainName
{!./docs/../samples/simple_app/app.py[ln:17]!}
{!./docs/../samples/simple_app/app.py[ln:18]!}


{!./docs/../samples/simple_app/app.py[ln:38-39]!}


{!./docs/../samples/simple_app/app.py[ln:62-74]!}


{!./docs/../samples/simple_app/app.py[ln:77-79]!}
    # more arguments to come
)
```


#### Saving Application Data

When Saleor is authorized to install the app an authentication key is issued, that key needs to be securely stored by the app as it provides as much access as the app requested in the manifest.

```python linenums="1" hl_lines="2 11-17 38"
{!./docs/../samples/simple_app/app.py[ln:9]!}
{!./docs/../samples/simple_app/app.py[ln:10]!}
{!./docs/../samples/simple_app/app.py[ln:17]!}
{!./docs/../samples/simple_app/app.py[ln:18]!}


{!./docs/../samples/simple_app/app.py[ln:38-48]!} #(1)


{!./docs/../samples/simple_app/app.py[ln:62-74]!}


{!./docs/../samples/simple_app/app.py[ln:77-80]!}
)
```

1. :material-database: Typically, you'd store all the data passed to this function to a DB table


#### Configuration URL

To finalize, you need to provide the endpoint named ```#!python configuration-form``` specified in the [#Manifest](#manifest).

```python linenums="1" hl_lines="1 3-4 8 48-100"
import json

{!./docs/../samples/simple_app/app.py[ln:4-5]!}

{!./docs/../samples/simple_app/app.py[ln:9]!}
{!./docs/../samples/simple_app/app.py[ln:10]!}
from saleor_app.deps import ConfigurationFormDeps
{!./docs/../samples/simple_app/app.py[ln:17]!}
{!./docs/../samples/simple_app/app.py[ln:18]!}


{!./docs/../samples/simple_app/app.py[ln:38-48]!} 


{!./docs/../samples/simple_app/app.py[ln:62-74]!}


{!./docs/../samples/simple_app/app.py[ln:77-80]!}
)


{!./docs/../samples/simple_app/app.py[ln:107-116]!}


{!./docs/../samples/simple_app/app.py[ln:124]!} #(1)
```

1. Once you are done defining all the configuration routes you need to tell the app to load them

> This is a complete example that will work as is.

!!! warning "Remember about `app.include_saleor_app_routes()`"

### Running the App

To run the app you can save the above example in `simple_app/app.py` and run it with:

```bash
uvicorn simple_app.app:app --host 0.0.0.0 --port 5000 --reload
```

Or create a `simple_app/__main__.py` with:

```python linenums="1" 
import uvicorn


def main():
    uvicorn.run(
        "simple_app.app:app", host="0.0.0.0", port=5000, debug=True, reload=True
    )


if __name__ == "__main__":
    main()
```

and run the module as a script with Python's `-m` flag:

```bash
python -m simple_app
```

## Examples

Visit the [:material-github: Samples directory](https://github.com/saleor/saleor-app-framework-python/tree/main/samples){ target=_blank } to check apps that were built as examples of how the framework can be used.
