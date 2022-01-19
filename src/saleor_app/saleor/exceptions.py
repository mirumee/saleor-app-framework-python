from typing import Any, Dict, Optional, Sequence


class GraphQLError(Exception):
    """
    Raised on Saleor GraphQL errors
    """

    def __init__(
        self,
        errors: Sequence[Dict[str, Any]],
        response_data: Optional[Dict[str, Any]] = None,
    ):
        self.errors = errors
        self.response_data = response_data

    def __str__(self):
        return (
            f"GraphQLError: {', '.join([error['message'] for error in self.errors])}."
        )
