from .graphql import get_executor, get_saleor_api_url

VERIFY_TOKEN = """
mutation TokenVerify($token: String!) {
  tokenVerify(token: $token){
    isValid
    user{
      id
    }
  }
}
"""


async def verify_token(saleor_domain: str, token: str) -> bool:
    api_url = get_saleor_api_url(saleor_domain)
    executor = get_executor(host=api_url, auth_token=None)
    response = await executor(
        VERIFY_TOKEN,
        variables={
            "token": token,
        },
    )

    try:
        return response["data"]["tokenVerify"]["isValid"] is True
    except KeyError:
        return False
