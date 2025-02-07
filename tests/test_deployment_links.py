from unittest.mock import MagicMock, patch
from bifrost_cli.commands.deployment_links import app


@patch("bifrost_cli.commands.deployment_links._make_request")
def test_deployment_links_success(
    mock_make_request, mock_asset_deployed_response, runner, mock_keyring
) -> None:
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_response_deploy = MagicMock()
    mock_response_deploy.status_code = 200
    mock_response_deploy.json.return_value = mock_asset_deployed_response
    mock_make_request.return_value = mock_response_deploy

    result = runner.invoke(
        app,
        ["--asset-id", "valid_asset_id"],
    )
    assert result.exit_code == 0
    assert "Successfully fetched asset deployment links" in result.stdout.replace("\n", "")

@patch("bifrost_cli.commands.deployment_links._make_request")
def test_no_deployment_links_success(
    mock_make_request, mock_asset_draft_response, runner, mock_keyring
) -> None:
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_response_deploy = MagicMock()
    mock_response_deploy.status_code = 200
    mock_response_deploy.json.return_value = mock_asset_draft_response
    mock_make_request.return_value = mock_response_deploy

    result = runner.invoke(
        app,
        ["--asset-id", "valid_asset_id"],
    )
    assert result.exit_code == 0
    assert "No deployment links found. The asset might not have been deployed yet." in result.stdout.replace("\n", "")

@patch("bifrost_cli.commands.deployment_links._make_request")
def test_deployment_links_failure(
    mock_make_request, runner, mock_keyring
) -> None:
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_response_deploy = MagicMock()
    mock_response_deploy.status_code = 400
    mock_response_deploy.json.return_value = None
    mock_make_request.return_value = mock_response_deploy

    result = runner.invoke(
        app,
        ["--asset-id", "valid_asset_id"],
    )
    assert result.exit_code == 0
    assert "❌ Failed to fetch asset." in result.stdout.replace("\n", "")