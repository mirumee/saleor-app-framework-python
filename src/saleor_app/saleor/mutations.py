CREATE_WEBHOOK = """
mutation WebhookCreate($input: WebhookCreateInput!) {
  webhookCreate(input: $input) {
    webhookErrors {
      field
      message
      code
    }
    webhook {
      id
    }
  }
}

"""

VERIFY_TOKEN = """
mutation TokenVerify($token: String!) {
  tokenVerify(token: $token) {
    isValid
    user {
      id
    }
  }
}

"""

VERIFY_APP_TOKEN = """
mutation AppTokenVerify($token: String!) {
  appTokenVerify(token: $token) {
    valid
  }
}

"""
