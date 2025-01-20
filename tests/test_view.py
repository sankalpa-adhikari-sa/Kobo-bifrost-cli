import pytest
from typer.testing import CliRunner
from bifrost_cli.commands.view import app as view_app
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
def mock_view_asset_snapshot_response():
    return {
        "enketopreviewlink": "https://eu.kobotoolbox.org/api/v2/asset_snapshots/snapshot_id/preview",
        "source": {"settings": {"form_title": "new"}},
    }


@patch("bifrost_cli.commands.view._make_request")
@patch("bifrost_cli.commands.view.update_asset_info")
def test_view_asset_snapshot_success(
    mock_update_asset_info,
    mock_make_request,
    runner,
    mock_keyring,
    mock_view_asset_snapshot_response,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_update_asset_info.return_value = None
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = mock_view_asset_snapshot_response
    mock_make_request.return_value = mock_response
    result = runner.invoke(
        view_app,
        [
            "--asset-id",
            "valid_asset_id",
        ],
    )
    assert result.exit_code == 0
    assert "✅ Successfully fetched asset snaphsots" in result.output


@patch("bifrost_cli.commands.view._make_request")
@patch("bifrost_cli.commands.view.update_asset_info")
def test_view_asset_snapshot_invalid_asset_id(
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
        view_app,
        [
            "--asset-id",
            "invalid_asset_id",
        ],
    )
    assert result.exit_code == 0
    assert "❌ Failed to fetch asset snapshot." in result.output
