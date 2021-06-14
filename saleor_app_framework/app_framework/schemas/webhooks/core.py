from pydantic import BaseModel


class InstallData(BaseModel):
    auth_token: str
