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
