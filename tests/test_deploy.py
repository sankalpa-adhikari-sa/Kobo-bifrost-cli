import pytest
from typer.testing import CliRunner
from bifrost_cli.commands.deploy import app
from unittest.mock import patch, MagicMock


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def isolated_filesystem(runner):
    with runner.isolated_filesystem() as fs:
        yield fs


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


@pytest.fixture
def mock_deploy_response():
    return {
        "asset": {
            "deployment_status": "deployed",
            "deployment__links": {
                "url": "https://",
                "single_url": "",
                "single_once_url": "https://",
                "offline_url": "https://",
                "preview_url": "https://",
                "iframe_url": "https://",
                "single_iframe_url": "https://",
                "single_once_iframe_url": "https://",
            },
        }
    }


@patch("bifrost_cli.commands.deploy._make_request")
def test_deploy_failure(mock_make_request, runner, mock_keyring):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_response_deploy = MagicMock()
    mock_response_deploy.status_code = 404
    mock_make_request.return_value = mock_response_deploy

    result = runner.invoke(
        app,
        ["--asset-id", "invalid_asset_id"],
    )
    assert result.exit_code == 0
    assert "Something went wrong!" in result.stdout

    mock_make_request.assert_called_once()


@patch("bifrost_cli.commands.deploy._make_request")
def test_deploy_failure_already_deployed(
    mock_make_request, runner, mock_keyring
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_make_request.return_value = None

    result = runner.invoke(
        app,
        ["--asset-id", "valid_asset_id"],
    )
    assert result.exit_code == 0
    assert (
        "\nError: The form you are trying to deploy may not exist or \n"
        "The form cannot be deployed as it may already be deployed."
        in result.stdout
    )

    mock_make_request.assert_called_once()


@patch("bifrost_cli.commands.deploy._make_request")
def test_deploy_success(
    mock_make_request, mock_deploy_response, runner, mock_keyring
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_response_deploy = MagicMock()
    mock_response_deploy.status_code = 200
    mock_response_deploy.json.return_value = mock_deploy_response
    mock_make_request.return_value = mock_response_deploy

    result = runner.invoke(
        app,
        ["--asset-id", "valid_asset_id"],
    )
    assert result.exit_code == 0
    assert "Successfully Deployed form" in result.stdout

    mock_make_request.assert_called_once()
