import pytest
from typer.testing import CliRunner
from bifrost_cli.commands.update import app as update_app
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
def mock_response():
    return {
        "messages": {
            "updated": [
                {
                    "uid": "aLzhec9AxLAVwXqsb6wq9g",
                    "kind": "asset",
                    "summary": {
                        "geo": True,
                        "labels": [
                            "Question 1",
                            "Question 2",
                            "Question 3",
                            "Question 4",
                            "Question 5",
                        ],
                        "columns": [
                            "type",
                            "name",
                            "label",
                            "hint",
                            "required",
                            "appearance",
                            "select_from_list_name",
                            "calculation",
                            "trigger",
                            "read_only",
                            "choice_filter",
                            "constraint",
                            "constraint_message",
                            "relevant",
                            "repeat_count",
                            "parameters",
                        ],
                        "lock_all": False,
                        "lock_any": False,
                        "languages": [],
                        "row_count": 682,
                        "name_quality": {
                            "ok": 1,
                            "bad": 0,
                            "good": 681,
                            "total": 682,
                            "firsts": {
                                "ok": {
                                    "name": "Suggestion_for_improvement",
                                    "index": 673,
                                    "label": ["Suggestion for improvement"],
                                }
                            },
                        },
                        "default_translation": None,
                    },
                    "owner__username": "some_user",
                }
            ]
        }
    }


@pytest.fixture
def mock_deploy_response():
    return {
        "asset": {
            "deployment_status": "deployed",
            "deployment__links": {
                "url": "https://",
                "single_url": "",
                "single_once_url": "https://",
                "offline_url": "https://",
                "preview_url": "https://",
                "iframe_url": "https://",
                "single_iframe_url": "https://",
                "single_once_iframe_url": "https://",
            },
        }
    }


@pytest.fixture
def mock_redeploy_response():
    return {
        "asset": {
            "version_count": "",
            "deployed_version_id": "",
            "deployment__submission_count": "",
            "deployment_status": "deployed",
            "deployment__links": {
                "url": "https://",
                "single_url": "",
                "single_once_url": "https://",
                "offline_url": "https://",
                "preview_url": "https://",
                "iframe_url": "https://",
                "single_iframe_url": "https://",
                "single_once_iframe_url": "https://",
            },
        }
    }


@pytest.fixture
def mock_version_id():
    return {"version_id": "valid_version_id"}


@patch("bifrost_cli.commands.update._import_form")
@patch("bifrost_cli.commands.update.update_asset_info")
def test_update_success(
    mock_update_asset_info,
    mock_import_form,
    runner,
    mock_keyring,
    mock_response,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_import_form.return_value = mock_response
    mock_update_asset_info.return_value = None
    result = runner.invoke(
        update_app,
        [
            "--asset-id",
            "valid_asset_id",
            "--filepath",
            "valid_filepath.xlsx",
        ],
    )
    assert result.exit_code == 0
    assert "✅ Successfully updated form" in result.output


@patch("bifrost_cli.commands.update._import_form")
@patch("bifrost_cli.commands.update.update_asset_info")
def test_update_failure(
    mock_update_asset_info, mock_import_form, runner, mock_keyring
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_import_form.return_value = None
    mock_update_asset_info.return_value = None
    result = runner.invoke(
        update_app,
        [
            "--asset-id",
            "valid_asset_id",
            "--filepath",
            "valid_filepath.xlsx",
        ],
    )

    assert result.exit_code == 0
    assert "❌ Failed to update form." in result.output


@patch("bifrost_cli.commands.deploy._make_request")
@patch("bifrost_cli.commands.update._import_form")
@patch("bifrost_cli.commands.update.update_asset_info")
def test_update_deploy_success(
    mock_update_asset_info,
    mock_import_form,
    mock_make_request,
    runner,
    mock_keyring,
    mock_response,
    mock_deploy_response,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_response_deploy = MagicMock()
    mock_response_deploy.status_code = 200
    mock_response_deploy.json.return_value = mock_deploy_response
    mock_make_request.return_value = mock_response_deploy

    mock_import_form.return_value = mock_response
    mock_update_asset_info.return_value = None
    result = runner.invoke(
        update_app,
        [
            "--asset-id",
            "valid_asset_id",
            "--filepath",
            "valid_filepath.xlsx",
            "-d",
        ],
    )

    assert result.exit_code == 0
    assert "✅ Successfully updated form" in result.output
    assert "✅ Successfully Deployed form" in result.output


@patch("bifrost_cli.commands.deploy._make_request")
@patch("bifrost_cli.commands.update._import_form")
@patch("bifrost_cli.commands.update.update_asset_info")
def test_update_deploy_failure(
    mock_update_asset_info,
    mock_import_form,
    mock_make_request,
    runner,
    mock_keyring,
    mock_response,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_response_deploy = MagicMock()
    mock_response_deploy.status_code = 404
    mock_make_request.return_value = mock_response_deploy

    mock_import_form.return_value = mock_response
    mock_update_asset_info.return_value = None
    result = runner.invoke(
        update_app,
        [
            "--asset-id",
            "valid_asset_id",
            "--filepath",
            "valid_filepath.xlsx",
            "-d",
        ],
    )

    assert result.exit_code == 0
    assert "✅ Successfully updated form" in result.output
    assert "Something went wrong!" in result.output


@patch("bifrost_cli.commands.deploy._make_request")
@patch("bifrost_cli.commands.update._import_form")
@patch("bifrost_cli.commands.update.update_asset_info")
def test_update_deploy_failure_already_deployed(
    mock_update_asset_info,
    mock_import_form,
    mock_make_request,
    runner,
    mock_keyring,
    mock_response,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_make_request.return_value = None

    mock_import_form.return_value = mock_response
    mock_update_asset_info.return_value = None
    result = runner.invoke(
        update_app,
        [
            "--asset-id",
            "valid_asset_id",
            "--filepath",
            "valid_filepath.xlsx",
            "-d",
        ],
    )

    assert result.exit_code == 0
    assert "✅ Successfully updated form" in result.output
    assert (
        "\nError: The form you are trying to deploy may not exist or \n"
        "The form cannot be deployed as it may already be deployed."
        in result.stdout
    )


@patch("bifrost_cli.commands.redeploy._make_request")
@patch("bifrost_cli.commands.update._import_form")
@patch("bifrost_cli.commands.update.update_asset_info")
def test_update_redeploy_success(
    mock_update_asset_info,
    mock_import_form,
    mock_make_request,
    runner,
    mock_keyring,
    mock_response,
    mock_redeploy_response,
    mock_version_id,
):
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

    mock_import_form.return_value = mock_response
    mock_update_asset_info.return_value = None
    result = runner.invoke(
        update_app,
        [
            "--asset-id",
            "valid_asset_id",
            "--filepath",
            "valid_filepath.xlsx",
            "-rd",
        ],
    )

    assert result.exit_code == 0
    assert "✅ Successfully updated form" in result.output
    assert "✅ Successfully Re-deployed form" in result.output


@patch("bifrost_cli.commands.redeploy._make_request")
@patch("bifrost_cli.commands.update._import_form")
@patch("bifrost_cli.commands.update.update_asset_info")
def test_update_redeploy_not_deployed(
    mock_update_asset_info,
    mock_import_form,
    mock_make_request,
    runner,
    mock_keyring,
    mock_response,
    mock_version_id,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_response_deploy1 = MagicMock()
    mock_response_deploy1.status_code = 200
    mock_response_deploy1.json.return_value = mock_version_id

    mock_make_request.side_effect = [
        mock_response_deploy1,
        None,
    ]

    mock_import_form.return_value = mock_response
    mock_update_asset_info.return_value = None
    result = runner.invoke(
        update_app,
        [
            "--asset-id",
            "valid_asset_id",
            "--filepath",
            "valid_filepath.xlsx",
            "-rd",
        ],
    )

    assert result.exit_code == 0
    assert "✅ Successfully updated form" in result.output
    assert (
        "Error: The form cannot be redeployed.\nPlease check the deployment status of the form"
        in result.output
    )


@patch("bifrost_cli.commands.redeploy._make_request")
@patch("bifrost_cli.commands.update._import_form")
@patch("bifrost_cli.commands.update.update_asset_info")
def test_update_redeploy_form_not_exist(
    mock_update_asset_info,
    mock_import_form,
    mock_make_request,
    runner,
    mock_keyring,
    mock_response,
    mock_version_id,
):
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_make_request.return_value = None

    mock_import_form.return_value = mock_response
    mock_update_asset_info.return_value = None
    result = runner.invoke(
        update_app,
        [
            "--asset-id",
            "valid_asset_id",
            "--filepath",
            "valid_filepath.xlsx",
            "-rd",
        ],
    )

    assert result.exit_code == 0
    assert "✅ Successfully updated form" in result.output
    assert (
        "Error: The form you are trying to redeploy may not exist."
        in result.output
    )
