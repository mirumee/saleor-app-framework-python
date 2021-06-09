# saleor-app-framework-python


## Tox 

To execeute tests with tox just invoke `tox` or `tox -p`. The tox-poetry plugin will read pyproject.toml and handle the envs creation. In case of a change in the dependencies you can force a recreation of the envs with `tox -r`.

One might also want to just run a specific testenv like: `tox -e coverage`.
To reduce the noisy output use `-q` like: `tox -p -q`
