from unittest.mock import MagicMock, patch

from bifrost_cli.commands.redeploy import app as redeploy_app


@patch("bifrost_cli.commands.redeploy._make_request")
def test_redeploy_success(
    mock_make_request,
    runner,
    mock_keyring,
    mock_redeploy_response,
    mock_version_id,
) -> None:
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
    assert "✅ Successfully Re-deployed form" in result.stdout


@patch("bifrost_cli.commands.redeploy._make_request")
def test_redeploy_failure(
    mock_make_request,
    runner,
    mock_keyring,
    mock_version_id,
) -> None:
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
    assert "Something went wrong!" in result.stdout


@patch("bifrost_cli.commands.redeploy._make_request")
def test_redeploy_not_deployed(
    mock_make_request,
    runner,
    mock_keyring,
    mock_version_id,
) -> None:
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_response_deploy1 = MagicMock()
    mock_response_deploy1.status_code = 200
    mock_response_deploy1.json.return_value = mock_version_id
    mock_response_deploy2 = MagicMock()
    mock_response_deploy2.status_code = 405

    mock_make_request.side_effect = [
        mock_response_deploy1,
        mock_response_deploy2,
    ]

    result = runner.invoke(
        redeploy_app,
        ["--asset-id", "valid_asset_id"],
    )

    assert result.exit_code == 0
    assert "Error: The form cannot be redeployed." in result.stdout.replace("\n", "")


@patch("bifrost_cli.commands.redeploy._make_request")
def test_redeploy_form_not_exist(
    mock_make_request,
    runner,
    mock_keyring,
) -> None:
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {
        "detail": "TThe form you are trying to redeploy may not exist."
    }
    mock_make_request.sideeffect = mock_response

    result = runner.invoke(
        redeploy_app,
        ["--asset-id", "valid_asset_id"],
    )

    assert result.exit_code == 0
    assert "Error: The form you are trying to redeploy may not exist." in result.stdout
