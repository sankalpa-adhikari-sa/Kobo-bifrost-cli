from unittest.mock import MagicMock, patch

from bifrost_cli.commands.deploy import app


@patch("bifrost_cli.commands.deploy._make_request")
def test_deploy_failure(mock_make_request, runner, mock_keyring) -> None:
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
    assert (
        "Error: The form you are trying to deploy may not exist or "
        "The form cannot be deployed as it may already be deployed."
        in result.stdout.replace("\n", "")
    )

    mock_make_request.assert_called_once()


@patch("bifrost_cli.commands.deploy._make_request")
def test_deploy_failure_already_deployed(
    mock_make_request, runner, mock_keyring
) -> None:
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_response_deploy = MagicMock()
    mock_response_deploy.status_code = 405
    mock_make_request.return_value = mock_response_deploy

    result = runner.invoke(
        app,
        ["--asset-id", "valid_asset_id"],
    )
    assert result.exit_code == 0
    assert (
        "Error: The form you are trying to deploy may not exist or "
        "The form cannot be deployed as it may already be deployed."
        in result.stdout.replace("\n", "")
    )

    mock_make_request.assert_called_once()


@patch("bifrost_cli.commands.deploy._make_request")
def test_deploy_success(
    mock_make_request, mock_deploy_response, runner, mock_keyring
) -> None:
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
