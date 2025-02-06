from unittest.mock import MagicMock, patch

from bifrost_cli.commands.preview import app as preview_app


@patch("bifrost_cli.commands.preview._make_request")
@patch("bifrost_cli.commands.preview.update_asset_info")
def test_preview_asset_snapshot_success(
    mock_update_asset_info,
    mock_make_request,
    runner,
    mock_keyring,
    mock_preview_asset_snapshot_response,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_update_asset_info.return_value = None
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = mock_preview_asset_snapshot_response
    mock_make_request.return_value = mock_response
    result = runner.invoke(
        preview_app,
        [
            "--asset-id",
            "valid_asset_id",
        ],
    )
    assert result.exit_code == 0
    assert "✅ Successfully fetched asset snapshots" in result.stdout


@patch("bifrost_cli.commands.preview._make_request")
@patch("bifrost_cli.commands.preview.update_asset_info")
def test_preview_asset_snapshot_invalid_asset_id(
    mock_update_asset_info,
    mock_make_request,
    runner,
    mock_keyring,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_update_asset_info.return_value = None

    mock_make_request.return_value = None
    result = runner.invoke(
        preview_app,
        [
            "--asset-id",
            "invalid_asset_id",
        ],
    )
    assert result.exit_code == 0
    assert "❌ Failed to fetch asset snapshot." in result.stdout
