class GraphQLBaseError(Exception):
    pass


class GraphQLError(GraphQLBaseError):
    """GraphQL Error"""


class InstallAppError(GraphQLBaseError):
    """Install App error"""
