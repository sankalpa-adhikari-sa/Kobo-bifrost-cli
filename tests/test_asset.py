import pytest
from typer.testing import CliRunner
from bifrost_cli.commands.asset import app as asset_app
from unittest.mock import patch, MagicMock
import os


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


@patch("bifrost_cli.commands.asset._make_request")
def test_asset_fail(
    mock_make_request, runner, mock_keyring, isolated_filesystem
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_make_request.return_value = None
    result = runner.invoke(
        asset_app, ["xls", "--asset-id", "invalid_asset_id"]
    )

    assert result.exit_code == 0
    assert "💥 Failed to download file." in result.output


@patch("bifrost_cli.commands.asset._make_request")
def test_asset_fail_downloadpath(
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
    assert "💥 Failed to download file." in result.output


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

    result = runner.invoke(
        asset_app,
        [
            "xls",
            "--asset-id",
            "invalid_asset_id",
            "--download-path",
            "invalid_path",
        ],
    )
    assert result.exit_code == 0
    assert (
        "Error: No such directory: invalid_path. "
        "Please check the path and try again."
        in result.output.replace("\n", "")
    )


@patch("bifrost_cli.commands.asset._make_request")
def test_asset_success(
    mock_make_request, runner, mock_keyring, isolated_filesystem
):
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

    expected_file_path = os.path.join(
        isolated_filesystem, "valid_asset_id.xlsx"
    )
    assert result.exit_code == 0
    assert "✅ File downloaded successfully and saved" in result.output
    with open(expected_file_path, "rb") as f:
        assert f.read() == b"Test file content"
