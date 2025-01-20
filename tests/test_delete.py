import pytest
from typer.testing import CliRunner
from bifrost_cli.commands.delete import app as delete
from unittest.mock import patch, MagicMock


@pytest.fixture
def runner():
    return CliRunner()


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


def test_delete_abort(runner, mock_keyring):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    result = runner.invoke(
        delete,
        ["--asset-id", "asset_id"],
        input="n\n",
    )

    assert result.exit_code == 1
    assert "Do you want to delete the project?" in result.output
    assert "Aborting project Deletion." in result.output
    assert "Aborted." in result.output


@patch("bifrost_cli.commands.delete._make_request")
def test_delete_fail(mock_make_request, runner, mock_keyring):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_make_request.return_value = None
    result = runner.invoke(
        delete,
        ["--asset-id", "invalid_asset_id"],
        input="y\n",
    )

    assert result.exit_code == 0
    assert "Do you want to delete the project?" in result.output
    assert "💥 Failed to Delete Form" in result.output


@patch("bifrost_cli.commands.delete._make_request")
def test_delete_success(mock_make_request, runner, mock_keyring):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_make_request.return_value = mock_response

    result = runner.invoke(
        delete,
        ["--asset-id", "valid_asset_id"],
        input="y\n",
    )

    assert result.exit_code == 0
    assert "Do you want to delete the project?" in result.output
    assert "✅ Succssfully Deleted Form" in result.output
