from pydantic import BaseModel


class InstallAppData(BaseModel):
    auth_token: str
