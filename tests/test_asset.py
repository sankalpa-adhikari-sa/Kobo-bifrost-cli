from pathlib import Path
from unittest.mock import MagicMock, patch

from bifrost_cli.commands.asset import app as asset_app


@patch("bifrost_cli.commands.asset._make_request")
def test_asset_fail_invalid_id(
    mock_make_request, runner, mock_keyring, isolated_filesystem
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_make_request.return_value = None
    result = runner.invoke(
        asset_app,
        [
            "xls",
            "--asset-id",
            "invalid_asset_id",
            "--download-path",
            isolated_filesystem,
        ],
    )

    assert result.exit_code == 0
    assert "💥 Failed to download file." in result.stdout


@patch("bifrost_cli.commands.asset._make_request")
def test_asset_fail_invalid_downloadpath(
    mock_make_request, runner, mock_keyring, isolated_filesystem
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_make_request.return_value = mock_response
    invalid_download_file_path = Path(isolated_filesystem) / "invalid_subdir"

    result = runner.invoke(
        asset_app,
        [
            "xls",
            "--asset-id",
            "invalid_asset_id",
            "--download-path",
            invalid_download_file_path,
        ],
    )
    assert result.exit_code == 0
    assert "Error: No such directory: " in result.stdout.replace("\n", "")


@patch("bifrost_cli.commands.asset._make_request")
def test_asset_success(mock_make_request, runner, mock_keyring, isolated_filesystem):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_response = MagicMock()
    mock_response.content = b"Test file content"
    mock_response.status_code = 200
    mock_make_request.return_value = mock_response

    result = runner.invoke(
        asset_app,
        [
            "xls",
            "--asset-id",
            "valid_asset_id",
            "--download-path",
            isolated_filesystem,
        ],
    )

    expected_file_path = Path(isolated_filesystem) / "valid_asset_id.xlsx"

    assert result.exit_code == 0
    assert "✅ File downloaded successfully and saved" in result.stdout
    with open(expected_file_path, "rb") as f:
        assert f.read() == b"Test file content"
