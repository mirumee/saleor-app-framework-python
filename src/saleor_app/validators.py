from saleor_app.graphql import get_executor, get_saleor_api_url
from saleor_app.mutations import VERIFY_TOKEN


async def verify_token(saleor_domain: str, token: str) -> bool:
    api_url = get_saleor_api_url(saleor_domain)
    executor = get_executor(host=api_url, auth_token=None)
    response, errors = await executor(
        VERIFY_TOKEN,
        variables={
            "token": token,
        },
    )
    if errors:
        return False
    try:
        return response["data"]["tokenVerify"]["isValid"] is True
    except KeyError:
        return False
