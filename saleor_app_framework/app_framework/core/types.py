from pydantic import BaseModel

DomainName = str
AppToken = str
Url = str


class InstallAppData(BaseModel):
    token: str
    webhook_id: str
    webhook_secret_key: str
