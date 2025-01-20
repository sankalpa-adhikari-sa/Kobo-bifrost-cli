import pytest
from typer.testing import CliRunner
from bifrost_cli.commands.auth import app
from unittest.mock import patch


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_keyring():
    with patch("keyring.get_password") as mock_get_password, patch(
        "keyring.set_password"
    ) as mock_set_password, patch(
        "keyring.delete_password"
    ) as mock_delete_password:

        mock_dict = {
            "get_password": mock_get_password,
            "set_password": mock_set_password,
            "delete_password": mock_delete_password,
        }

        mock_get_password.return_value = None

        yield mock_dict


SERVICE_NAME = "kobo-bifrost"


def test_login_without_existing_credentials(runner, mock_keyring):
    mock_keyring["get_password"].return_value = None

    result = runner.invoke(
        app,
        ["set-credentials", "--api-key", "1234", "--api-url", "www.test.com"],
    )
    assert result.exit_code == 0
    assert "Credentials saved securely." in result.stdout


def test_login_with_credentials_override(runner, mock_keyring):
    mock_keyring["get_password"].side_effect = [
        "previous-api-key",
        "previous-api-url",
    ]
    result = runner.invoke(
        app,
        ["set-credentials", "--api-key", "1234", "--api-url", "www.test.com"],
        input="y\n",
    )
    assert result.exit_code == 0
    mock_keyring["set_password"].assert_any_call(
        "kobo-bifrost", "api_key", "1234"
    )
    mock_keyring["set_password"].assert_any_call(
        "kobo-bifrost", "api_url", "www.test.com"
    )
    assert "Credentials saved securely." in result.stdout


def test_login_with_credentials_no_overrride(runner, mock_keyring):
    mock_keyring["get_password"].side_effect = ["api-key", "api-url"]
    result = runner.invoke(
        app,
        ["set-credentials", "--api-key", "1234", "--api-url", "www.test.com"],
        input="n\n",
    )
    assert result.exit_code == 0
    assert "Existing credentials retained. No changes made." in result.stdout
    mock_keyring["set_password"].assert_not_called()


def test_login_interactive(runner, mock_keyring):
    mock_keyring["get_password"].return_value = None
    result = runner.invoke(
        app, ["set-credentials"], input="1234\nwww.test.com\n"
    )
    assert result.exit_code == 0
    assert "Credentials saved securely." in result.stdout
    mock_keyring["set_password"].assert_any_call(
        "kobo-bifrost", "api_key", "1234"
    )
    mock_keyring["set_password"].assert_any_call(
        "kobo-bifrost", "api_url", "www.test.com"
    )


def test_login_interactive_override(runner, mock_keyring):
    mock_keyring["get_password"].side_effect = [
        "previous-api-key",
        "previous-api-url",
    ]
    result = runner.invoke(
        app, ["set-credentials"], input="y\n1234\nwww.test.com\n"
    )
    assert result.exit_code == 0
    assert "Credentials saved securely." in result.stdout
    mock_keyring["set_password"].assert_any_call(
        "kobo-bifrost", "api_key", "1234"
    )
    mock_keyring["set_password"].assert_any_call(
        "kobo-bifrost", "api_url", "www.test.com"
    )


def test_logout_with_credentials(runner, mock_keyring):
    mock_keyring["get_password"].side_effect = [
        "previous-api-key",
        "previous-api-url",
    ]
    result = runner.invoke(app, ["remove-credentials"])
    assert result.exit_code == 0
    assert "Credentials removed." in result.stdout
    mock_keyring["delete_password"].assert_any_call(SERVICE_NAME, "api_key")
    mock_keyring["delete_password"].assert_any_call(SERVICE_NAME, "api_url")


def test_logout_without_credentials(runner, mock_keyring):

    def get_password_side_effect(service_name, key):
        return None

    mock_keyring["get_password"].side_effect = get_password_side_effect
    result = runner.invoke(app, ["remove-credentials"])
    assert result.exit_code == 0
    assert "No credentials were found to delete." in result.stdout
    assert mock_keyring["delete_password"].call_count == 0
    mock_keyring["get_password"].assert_any_call(SERVICE_NAME, "api_key")
    mock_keyring["get_password"].assert_any_call(SERVICE_NAME, "api_url")
