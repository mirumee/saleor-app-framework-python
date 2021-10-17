# saleor-app-framework-python


## Tox 

To execeute tests with tox just invoke `tox` or `tox -p`. The tox-poetry plugin will read pyproject.toml and handle the envs creation. In case of a change in the dependencies you can force a recreation of the envs with `tox -r`.

One might also want to just run a specific testenv like: `tox -e coverage`.
To reduce the noisy output use `-q` like: `tox -p -q`

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
