# Single Tenant App

This is an example Saleor App that is supposed to handle only one Saleor instance - single tenant - by design. A usecase of an app like this might be a custom Saleor interface for your existing infrastructure - this app will be able to receive webhook domain events, and execute calls to Saleor.


## Prerequisites

Install all dependencies from the Saleor App package

```
poetry install
```

## Running the sample service

```
cd samples
python -m single_tenant_app
```
