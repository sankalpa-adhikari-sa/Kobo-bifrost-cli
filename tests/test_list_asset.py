import pytest
from typer.testing import CliRunner
from bifrost_cli.commands.list_asset import app
from unittest.mock import patch, MagicMock


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_keyring():
    with patch("keyring.get_password") as mock_get_password, patch(
        "keyring.set_password"
    ) as mock_set_password:
        mock_get_password.return_value = "test-value"
        yield {
            "get_password": mock_get_password,
            "set_password": mock_set_password,
        }


SERVICE_NAME = "kobo-bifrost"


@patch("bifrost_cli.commands.list_asset._make_request")
def test_list_asset(
    mock_make_request,
    mock_keyring,
    runner,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "name": "Project A",
                "uid": "123",
                "deployment_status": "Active",
                "deployed_version_id": 1,
                "version_id": 1,
                "deployment__submission_count": 5,
            },
            {
                "name": "Project B",
                "uid": "456",
                "deployment_status": "Inactive",
                "deployed_version_id": None,
                "version_id": 2,
                "deployment__submission_count": 0,
            },
        ]
    }
    mock_make_request.return_value = mock_response

    result = runner.invoke(app)

    assert result.exit_code == 0
    assert "List of Assets" in result.output
