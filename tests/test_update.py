from unittest.mock import MagicMock, patch

from bifrost_cli.commands.update import app as update_app


@patch("bifrost_cli.commands.update._import_form")
@patch("bifrost_cli.commands.update.update_asset_info")
def test_update_success(
    mock_update_asset_info,
    mock_import_form,
    runner,
    mock_keyring,
    mock_import_update_response,
) -> None:
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_import_form.return_value = mock_import_update_response
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
    assert "✅ Successfully updated form" in result.stdout


@patch("bifrost_cli.commands.update._import_form")
@patch("bifrost_cli.commands.update.update_asset_info")
def test_update_failure(
    mock_update_asset_info, mock_import_form, runner, mock_keyring
) -> None:
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
    assert "❌ Failed to update form." in result.stdout


def test_update_with_deploy_and_redeploy(runner) -> None:
    """Test that providing both --deploy and --redeploy raises an error."""
    result = runner.invoke(
        update_app,
        [
            "--asset-id",
            "valid_asset_id",
            "--filepath",
            "valid_filepath.xlsx",
            "-d",
            "-rd",
        ],
    )

    assert result.exit_code != 0

    assert "Error: You cannot specify both " in result.stdout.replace("\n", "")


@patch("bifrost_cli.commands.deploy._make_request")
@patch("bifrost_cli.commands.update._import_form")
@patch("bifrost_cli.commands.update.update_asset_info")
def test_update_deploy_success(
    mock_update_asset_info,
    mock_import_form,
    mock_make_request,
    runner,
    mock_keyring,
    mock_import_update_response,
    mock_deploy_response,
) -> None:
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_response_deploy = MagicMock()
    mock_response_deploy.status_code = 200
    mock_response_deploy.json.return_value = mock_deploy_response
    mock_make_request.return_value = mock_response_deploy

    mock_import_form.return_value = mock_import_update_response
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
    assert "✅ Successfully updated form" in result.stdout
    assert "✅ Successfully Deployed form" in result.stdout


@patch("bifrost_cli.commands.deploy._make_request")
@patch("bifrost_cli.commands.update._import_form")
@patch("bifrost_cli.commands.update.update_asset_info")
def test_update_deploy_failure(
    mock_update_asset_info,
    mock_import_form,
    mock_make_request,
    runner,
    mock_keyring,
    mock_import_update_response,
) -> None:
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_response_deploy = MagicMock()
    mock_response_deploy.status_code = 404
    mock_make_request.return_value = mock_response_deploy

    mock_import_form.return_value = mock_import_update_response
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
    assert "✅ Successfully updated form" in result.stdout
    assert (
        "Error: The form you are trying to deploy may not exist or "
        "The form cannot be deployed as it may already be deployed."
        in result.stdout.replace("\n", "")
    )


@patch("bifrost_cli.commands.deploy._make_request")
@patch("bifrost_cli.commands.update._import_form")
@patch("bifrost_cli.commands.update.update_asset_info")
def test_update_deploy_failure_already_deployed(
    mock_update_asset_info,
    mock_import_form,
    mock_make_request,
    runner,
    mock_keyring,
    mock_import_update_response,
) -> None:
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_make_request.return_value = None

    mock_import_form.return_value = mock_import_update_response
    mock_response_deploy = MagicMock()
    mock_response_deploy.status_code = 405
    mock_make_request.return_value = mock_response_deploy
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
    assert "✅ Successfully updated form" in result.stdout
    assert (
        "Error: The form you are trying to deploy may not exist or "
        "The form cannot be deployed as it may already be deployed."
        in result.stdout.replace("\n", "")
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
    mock_import_update_response,
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

    mock_import_form.return_value = mock_import_update_response
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
    assert "✅ Successfully updated form" in result.stdout
    assert "✅ Successfully Re-deployed form" in result.stdout


@patch("bifrost_cli.commands.redeploy._make_request")
@patch("bifrost_cli.commands.update._import_form")
@patch("bifrost_cli.commands.update.update_asset_info")
def test_update_redeploy_not_deployed(
    mock_update_asset_info,
    mock_import_form,
    mock_make_request,
    runner,
    mock_keyring,
    mock_import_update_response,
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

    mock_import_form.return_value = mock_import_update_response
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
    assert "✅ Successfully updated form" in result.stdout
    assert (
        "Error: The form cannot be redeployed.\nPlease check the deployment status of the form"
        in result.stdout
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
    mock_import_update_response,
    mock_version_id,
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

    mock_import_form.return_value = mock_import_update_response
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
    assert "✅ Successfully updated form" in result.stdout
    assert "Error: The form you are trying to redeploy may not exist." in result.stdout


@patch("bifrost_cli.commands.view._make_request")
@patch("bifrost_cli.commands.update._import_form")
@patch("bifrost_cli.commands.update.update_asset_info")
def test_update_preview_success(
    mock_update_asset_info,
    mock_import_form,
    mock_make_request,
    runner,
    mock_keyring,
    mock_import_update_response,
    mock_view_asset_snapshot_response,
) -> None:
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_response_preview = MagicMock()
    mock_response_preview.status_code = 201
    mock_response_preview.json.return_value = mock_view_asset_snapshot_response
    mock_make_request.return_value = mock_response_preview

    mock_import_form.return_value = mock_import_update_response
    mock_update_asset_info.return_value = None
    result = runner.invoke(
        update_app,
        [
            "--asset-id",
            "valid_asset_id",
            "--filepath",
            "valid_filepath.xlsx",
            "-ps",
        ],
    )

    assert result.exit_code == 0
    assert "✅ Successfully updated form" in result.stdout
    assert "✅ Successfully fetched asset snapshots" in result.stdout


@patch("bifrost_cli.commands.view._make_request")
@patch("bifrost_cli.commands.update._import_form")
@patch("bifrost_cli.commands.update.update_asset_info")
def test_update_asset_snapshot_invalid_asset_id(
    mock_update_asset_info,
    mock_import_form,
    mock_make_request,
    runner,
    mock_keyring,
    mock_import_update_response,
    mock_view_asset_snapshot_response,
) -> None:
    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    mock_make_request.return_value = None

    mock_import_form.return_value = mock_import_update_response
    mock_update_asset_info.return_value = None
    result = runner.invoke(
        update_app,
        [
            "--asset-id",
            "valid_asset_id",
            "--filepath",
            "valid_filepath.xlsx",
            "-ps",
        ],
    )

    assert result.exit_code == 0
    assert "✅ Successfully updated form" in result.stdout
    assert "❌ Failed to fetch asset snapshot." in result.stdout
