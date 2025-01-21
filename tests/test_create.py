import pytest
from typer.testing import CliRunner
from bifrost_cli.commands.create import app
from unittest.mock import patch, MagicMock
import os


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def isolated_filesystem(runner):
    with runner.isolated_filesystem() as fs:
        yield fs


@pytest.fixture
def mock_view_asset_snapshot_response():
    return {
        "enketopreviewlink": "https://eu.kobotoolbox.org/api/v2/asset_snapshots/snapshot_id/preview",
        "source": {"settings": {"form_title": "new"}},
    }


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
def mock_response():
    return {
        "status": "complete",
        "uid": "iEq4FGzZkLFKn33ZhkwEFi",
        "messages": {
            "created": [
                {
                    "uid": "aLgFhiUU9SECuWh2Q8oHtg",
                    "kind": "asset",
                    "summary": {"languages": []},
                    "owner__username": "some_user",
                }
            ]
        },
        "date_created": "2024-12-25T09:30:50.899133Z",
    }


@pytest.fixture
def mock_deploy_response():
    return {
        "asset": {
            "deployment_status": "deployed",
            "deployment__links": {
                "url": "https://",
                "single_url": "https:",
                "single_once_url": "https://",
                "offline_url": "https://",
                "preview_url": "https://",
                "iframe_url": "https://",
                "single_iframe_url": "https://",
                "single_once_iframe_url": "https://",
            },
        }
    }


@patch("bifrost_cli.commands.create._import_form")
@patch("bifrost_cli.commands.create.update_asset_info")
def test_create_success(
    mock_update_asset_info,
    mock_import_form,
    mock_response,
    runner,
    mock_keyring,
    isolated_filesystem,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_import_form.return_value = mock_response
    mock_update_asset_info.return_value = None
    result = runner.invoke(
        app,
        ["--filepath", isolated_filesystem],
    )
    assert result.exit_code == 0
    assert "Information of created asset" in result.stdout
    assert "aLgFhiUU9SECuWh2Q8oHtg" in result.stdout
    mock_import_form.assert_called_once()


@patch("bifrost_cli.commands.view._make_request")
@patch("bifrost_cli.commands.create._import_form")
@patch("bifrost_cli.commands.create.update_asset_info")
def test_create_preview_success(
    mock_update_asset_info,
    mock_import_form,
    mock_make_request,
    mock_response,
    runner,
    mock_keyring,
    isolated_filesystem,
    mock_view_asset_snapshot_response,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_response_preview = MagicMock()
    mock_response_preview.status_code = 201
    mock_response_preview.json.return_value = mock_view_asset_snapshot_response
    mock_make_request.return_value = mock_response_preview

    mock_import_form.return_value = mock_response
    mock_update_asset_info.return_value = None
    result = runner.invoke(
        app,
        [
            "--filepath",
            isolated_filesystem,
            "-ps",
        ],
    )
    assert result.exit_code == 0
    assert "Information of created asset" in result.stdout
    assert "aLgFhiUU9SECuWh2Q8oHtg" in result.stdout
    assert "✅ Successfully fetched asset snaphsots" in result.output
    mock_import_form.assert_called_once()


@patch("bifrost_cli.commands.view._make_request")
@patch("bifrost_cli.commands.create._import_form")
@patch("bifrost_cli.commands.create.update_asset_info")
def test_create_preview_failure(
    mock_update_asset_info,
    mock_import_form,
    mock_make_request,
    mock_response,
    runner,
    mock_keyring,
    isolated_filesystem,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_make_request.return_value = None

    mock_import_form.return_value = mock_response
    mock_update_asset_info.return_value = None
    result = runner.invoke(
        app,
        [
            "--filepath",
            isolated_filesystem,
            "-ps",
        ],
    )
    assert result.exit_code == 0
    assert "Information of created asset" in result.stdout
    assert "aLgFhiUU9SECuWh2Q8oHtg" in result.stdout
    assert "❌ Failed to fetch asset snapshot." in result.output
    mock_import_form.assert_called_once()


@patch("bifrost_cli.commands.create._import_form")
@patch("bifrost_cli.commands.create.update_asset_info")
def test_create_failure(
    mock_update_asset_info,
    mock_import_form,
    runner,
    mock_keyring,
    isolated_filesystem,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_import_form.return_value = None
    mock_update_asset_info.return_value = None
    result = runner.invoke(
        app,
        ["--filepath", isolated_filesystem],
    )

    assert result.exit_code == 0
    assert "Failed to create form" in result.stdout


def test_create_invalid_file(runner, mock_keyring, isolated_filesystem):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    result = runner.invoke(
        app,
        ["--filepath", isolated_filesystem],
    )
    assert result.exit_code == 0
    assert (
        "Error: The file must be an .xls or .xlsx form. "
        "Please provide a valid file path." in result.stdout.replace("\n", "")
    )
    assert "Failed to create form" in result.stdout


def test_create_no_file(runner, mock_keyring, isolated_filesystem):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    file_path = os.path.join(isolated_filesystem, "test.xlsx")

    result = runner.invoke(
        app,
        ["--filepath", file_path],
    )
    assert result.exit_code == 0

    assert f"Error: File not found at {file_path}." in result.stdout
    assert "Failed to create form" in result.stdout


@patch("bifrost_cli.commands.create.create_form")
@patch("bifrost_cli.commands.deploy._make_request")
@patch("bifrost_cli.commands.create.update_asset_info")
def test_create_deploy_success(
    mock_update_asset_info,
    mock_make_request,
    mock_create_form,
    mock_deploy_response,
    runner,
    mock_keyring,
    isolated_filesystem,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_create_form.return_value = "aLgFhiUU9SECuWh2Q8oHtg"

    mock_response_deploy = MagicMock()
    mock_response_deploy.status_code = 200
    mock_response_deploy.json.return_value = mock_deploy_response
    mock_make_request.return_value = mock_response_deploy
    mock_update_asset_info.return_value = None

    result = runner.invoke(
        app,
        ["--filepath", isolated_filesystem, "-d"],
    )
    assert result.exit_code == 0
    assert "Successfully Deployed form" in result.stdout
    assert "aLgFhiUU9SECuWh2Q8oHtg" in result.stdout
    mock_create_form.assert_called_once()
    mock_make_request.assert_called_once()


@patch("bifrost_cli.commands.create.create_form")
@patch("bifrost_cli.commands.deploy._make_request")
@patch("bifrost_cli.commands.create.update_asset_info")
def test_create_deploy_failure(
    mock_update_asset_info,
    mock_make_request,
    mock_create_form,
    runner,
    mock_keyring,
    isolated_filesystem,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_create_form.return_value = "aLgFhiUU9SECuWh2Q8oHtg"

    mock_response_deploy = MagicMock()
    mock_response_deploy.status_code = 404
    mock_make_request.return_value = mock_response_deploy
    mock_update_asset_info.return_value = None

    result = runner.invoke(
        app,
        ["--filepath", isolated_filesystem, "-d"],
    )
    assert result.exit_code == 0
    assert "Something went wrong!" in result.stdout

    mock_create_form.assert_called_once()
    mock_make_request.assert_called_once()
