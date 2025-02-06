from unittest.mock import MagicMock, patch

from bifrost_cli.commands.permissions import app as permissions_app


@patch("bifrost_cli.commands.permissions._make_request")
def test_set_permission_success(mock_make_request, mock_keyring, runner):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_make_request.return_value = mock_response
    result = runner.invoke(
        permissions_app,
        ["set-permissions", "--asset-id", "valid_asset_id", "--no-auth-sub"],
    )

    assert result.exit_code == 0
    assert (
        "✅ Successfully updated permission to submit data without auth."
        in result.stdout
    )


@patch("bifrost_cli.commands.permissions._make_request")
def test_set_permission_failure(mock_make_request, mock_keyring, runner):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_make_request.return_value = mock_response
    result = runner.invoke(
        permissions_app,
        ["set-permissions", "--asset-id", "invalid_asset_id", "--no-auth-sub"],
    )

    assert result.exit_code == 0
    assert "💥 Failed to set permissions.\n" in result.stdout


@patch("bifrost_cli.commands.permissions._make_request")
def test_clone_permission_failure(mock_make_request, mock_keyring, runner):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = None
    mock_make_request.return_value = mock_response
    result = runner.invoke(
        permissions_app,
        [
            "clone-permissions",
            "--from",
            "valid_from_id",
            "--to",
            "valid_to_id",
        ],
    )

    assert result.exit_code == 0
    assert ("💥 Failed to clone permission.") in result.stdout


@patch("bifrost_cli.commands.permissions._make_request")
def test_clone_permission_success(mock_make_request, mock_keyring, runner):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_make_request.return_value = mock_response
    result = runner.invoke(
        permissions_app,
        [
            "clone-permissions",
            "--from",
            "valid_from_id",
            "--to",
            "valid_to_id",
        ],
    )

    assert result.exit_code == 0
    assert "✅ Successfully cloned permission" in result.stdout
