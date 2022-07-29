# saleor-app-framework-python

Saleor App Framework (Python) provides an easy way to install Your app into the [Saleor Commerce](https://github.com/saleor/saleor).

Supported features:

- Installation
- Webhooks handling
- Exception handling
- Ignoring Webhooks triggered by your app

More on usage You can find in the official [Documentation](https://mirumee.github.io/saleor-app-framework-python/)

## Installation

To use saleor app framework simply install it by

Using [poetry](https://python-poetry.org/)

```
poetry add git+https://github.com/saleor/saleor-app-framework-python.git@main
```

Using pip

```
pip install git+https://github.com/saleor/saleor-app-framework-python.git@main
```

## Usage

The recommended way of building Saleor Python Applications using this framework, is to use project template from [saleor-app-template](https://github.com/mirumee/saleor-app-template). This template will save You a lot of time configuring Your project.

It is preconfigured to use:

- uvicorn [[and gunicorn](https://gunicorn.org/)] - as HTTP server
- [SQLAlchemy](https://docs.sqlalchemy.org/en/14/core/) - as an ORM
- [alembic](https://alembic.sqlalchemy.org/en/latest/) - as a database migration tool with configured migration names, black and isort
- [encode/databases](https://www.encode.io/databases/) - as an asyncio support for SQLAlchemy
- [pytest](https://docs.pytest.org/en/7.1.x/) - for unit tests
- [poetry](https://python-poetry.org/) - as python package manager

With this template You will get:

- working Dockerfile and docker-compose.yaml
- working database with async support
- working configured tests
- working Saleor installation process

You can always develop Your own application from scratch, basing on the steps from [Documentation](https://mirumee.github.io/saleor-app-framework-python/) or change any of the existing tools.

<br/>

## Development

### Tox

To execeute tests with tox just invoke `tox` or `tox -p`. The tox-poetry plugin will read pyproject.toml and handle the envs creation. In case of a change in the dependencies you can force a recreation of the envs with `tox -r`.

One might also want to just run a specific testenv like: `tox -e coverage`.
To reduce the noisy output use `-q` like: `tox -p -q`

<br/>

## Deployment

#### Gunicorn

Here's an example `gunicorn.conf.py` file:

```python
from my_app.settings import LOGGING

workers = 2
keepalive = 30
worker_class = "uvicorn.workers.UvicornH11Worker"
bind = ["0.0.0.0:8080"]

accesslog = "-"
errorlog = "-"
loglevel = "info"
logconfig_dict = LOGGING

forwarded_allow_ips = "*"
```

It's a good starting point, keeps the log config in one place and includes the very important (`forwarded_allow_ips` flag)[https://docs.gunicorn.org/en/stable/settings.html#forwarded-allow-ips] **this flag needs to be understood when deploying your app** - it's not always safe to set it to `*` but in some setups it's the only option to allow FastAPI to generate proper urls with `url_for`.
