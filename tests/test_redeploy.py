import pytest
from typer.testing import CliRunner
from bifrost_cli.commands.redeploy import app as redeploy_app
from unittest.mock import patch, MagicMock


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def isolated_filesystem(runner):
    with runner.isolated_filesystem() as fs:
        yield fs


@pytest.fixture
def mock_redeploy_response():
    return {
        "asset": {
            "version_count": "",
            "deployed_version_id": "",
            "deployment__submission_count": "",
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


@pytest.fixture
def mock_version_id():
    return {"version_id": "valid_version_id"}


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


@patch("bifrost_cli.commands.redeploy._make_request")
def test_redeploy_success(
    mock_make_request,
    runner,
    mock_keyring,
    mock_redeploy_response,
    mock_version_id,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_response_deploy1 = MagicMock()
    mock_response_deploy1.status_code = 200
    mock_response_deploy1.json.return_value = mock_version_id

    mock_response_deploy2 = MagicMock()
    mock_response_deploy2.status_code = 200
    mock_response_deploy2.json.return_value = mock_redeploy_response

    mock_make_request.side_effect = [
        mock_response_deploy1,
        mock_response_deploy2,
    ]

    result = runner.invoke(
        redeploy_app,
        ["--asset-id", "valid_asset_id"],
    )

    assert result.exit_code == 0
    assert "✅ Successfully Re-deployed form" in result.output


@patch("bifrost_cli.commands.redeploy._make_request")
def test_redeploy_failure(
    mock_make_request,
    runner,
    mock_keyring,
    mock_version_id,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_response_deploy1 = MagicMock()
    mock_response_deploy1.status_code = 200
    mock_response_deploy1.json.return_value = mock_version_id

    mock_response_deploy2 = MagicMock()
    mock_response_deploy2.status_code = 400

    mock_make_request.side_effect = [
        mock_response_deploy1,
        mock_response_deploy2,
    ]

    result = runner.invoke(
        redeploy_app,
        ["--asset-id", "valid_asset_id"],
    )

    assert result.exit_code == 0
    assert "Something went wrong!" in result.output


@patch("bifrost_cli.commands.redeploy._make_request")
def test_redeploy_not_deployed(
    mock_make_request,
    runner,
    mock_keyring,
    mock_version_id,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_response_deploy1 = MagicMock()
    mock_response_deploy1.status_code = 200
    mock_response_deploy1.json.return_value = mock_version_id

    mock_make_request.side_effect = [
        mock_response_deploy1,
        None,
    ]

    result = runner.invoke(
        redeploy_app,
        ["--asset-id", "valid_asset_id"],
    )

    assert result.exit_code == 0
    assert (
        "Error: The form cannot be redeployed.Please check the deployment status of the form and ensure it is deployed before attempting to redeploy."
        in result.output.replace("\n", "")
    )


@patch("bifrost_cli.commands.redeploy._make_request")
def test_redeploy_form_not_exist(
    mock_make_request,
    runner,
    mock_keyring,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_make_request.return_value = None

    result = runner.invoke(
        redeploy_app,
        ["--asset-id", "valid_asset_id"],
    )

    assert result.exit_code == 0
    assert (
        "Error: The form you are trying to redeploy may not exist."
        in result.output
    )
