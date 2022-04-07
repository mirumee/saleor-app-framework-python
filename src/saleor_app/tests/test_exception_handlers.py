import pytest

from saleor_app.exception_handlers import IgnoredIssuingPrincipalChecker
from saleor_app.saleor.exceptions import IgnoredPrincipal


async def test_ignored_issuing_principal_checker_raise_exception(
    mock_request_with_metadata,
):
    ignored_issuing_app_principal = IgnoredIssuingPrincipalChecker(["VXNlcjox"])
    with pytest.raises(IgnoredPrincipal):
        await ignored_issuing_app_principal(mock_request_with_metadata)


async def test_ignored_issuing_principal_checker_without_raise_exception(
    mock_request_with_metadata,
):
    ignored_issuing_app_principal = IgnoredIssuingPrincipalChecker(["dummy-id"])
    try:
        await ignored_issuing_app_principal(mock_request_with_metadata)
    except IgnoredPrincipal:
        assert False
