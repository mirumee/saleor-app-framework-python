from typing import Optional

from pydantic import BaseSettings


class AWSSettings(BaseSettings):
    account_id: str
    access_key_id: str
    secret_access_key: str
    region: str
    endpoint_url: Optional[str]

    class Config:
        env_prefix = "AWS_"
