# Running everything locally

## Development mode

For local development and testing you can trick the app to use a Saleor that is not behind HTTPS and also force an auth token. **You shouldn't do neither in a production environment!**.

```python
from pydantic import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    development_auth_token: Optional[str] = None


settings = Settings(
    debug=True,
    development_auth_token="test_token",
)


app = SaleorApp(
    # [...]
    use_insecure_saleor_http=settings.debug,
    development_auth_token=settings.development_auth_token,
)
```

## Developing Apps on a local Saleor

Coming soon...
