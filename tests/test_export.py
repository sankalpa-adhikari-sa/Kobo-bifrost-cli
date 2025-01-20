import pytest
from typer.testing import CliRunner
from bifrost_cli.commands.export import app as export_app
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


@pytest.fixture
def mock_make_request_response():
    return {
        "url": "https://",
        "status": "created",
        "messages": {},
        "uid": "valid_asset_id",
        "date_created": "2025-01-14T11:30:55.778122Z",
        "last_submission_time": None,
        "result": None,
        "data": {
            "fields_from_all_versions": "True",
            "group_sep": "/",
            "hierarchy_in_labels": "False",
            "lang": "_default",
            "multiple_select": "summary",
            "source": "https://",
            "name": None,
            "type": "csv",
            "xls_types_as_text": "False",
            "include_media_url": "True",
        },
    }


@pytest.fixture
def mock_wait_for_completion_response():
    return {
        "url": "https://",
        "status": "complete",
        "messages": {},
        "uid": "valid_asset_id",
        "date_created": "2025-01-14T11:34:33.527217Z",
        "last_submission_time": None,
        "result": "https://",
        "data": {
            "lang": "_default",
            "name": None,
            "type": "csv",
            "source": "https://",
            "group_sep": "/",
            "multiple_select": "summary",
            "include_media_url": "True",
            "xls_types_as_text": "False",
            "hierarchy_in_labels": "False",
            "processing_time_seconds": 0.302638,
            "fields_from_all_versions": "True",
        },
    }


@pytest.fixture
def mock_file_content():
    return b"test,data\n1,2\n3,4"


@patch("bifrost_cli.commands.export._make_request")
@patch("bifrost_cli.commands.export._wait_for_completion")
def test_export_success(
    mock_wait_for_completion,
    mock_make_request,
    runner,
    mock_keyring,
    mock_file_content,
    mock_make_request_response,
    mock_wait_for_completion_response,
    isolated_filesystem,
):

    mock_response1 = MagicMock()
    mock_response1.json.return_value = mock_make_request_response

    mock_response2 = MagicMock()
    mock_response2.status_code = 200
    mock_response2.content = mock_file_content

    mock_make_request.side_effect = [mock_response1, mock_response2]

    mock_wait_for_completion.return_value = mock_wait_for_completion_response

    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    output_file = os.path.join(isolated_filesystem, "my_file.csv")

    result = runner.invoke(
        export_app,
        [
            "csv",
            "--asset-id",
            "valid_asset_id",
            "--output-name",
            "my_file",
        ],
    )

    assert result.exit_code == 0
    assert (
        f"File downloaded successfully and saved to {output_file}"
        in result.output
    )
    with open(output_file, "rb") as f:
        assert f.read() == mock_file_content

    assert mock_make_request.call_count == 2
    assert mock_wait_for_completion.call_count == 1
