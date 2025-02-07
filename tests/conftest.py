from unittest.mock import patch

import pytest
from typer.testing import CliRunner


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
    ) as mock_set_password, patch("keyring.delete_password") as mock_delete_password:

        mock_dict = {
            "get_password": mock_get_password,
            "set_password": mock_set_password,
            "delete_password": mock_delete_password,
        }

        mock_get_password.return_value = "test-value"

        yield mock_dict


SERVICE_NAME = "kobo-bifrost"


@pytest.fixture
def mock_preview_asset_snapshot_response():
    return {
        "enketopreviewlink": "https://eu.kobotoolbox.org/api/v2/asset_snapshots/snapshot_id/preview",
        "source": {"settings": {"form_title": "new"}},
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

@pytest.fixture
def mock_asset_deployed_response():
    return {
    "deployment__links": {
        "url": "",
        "single_url": "",
        "single_once_url": "",
        "offline_url": "",
        "preview_url": "",
        "iframe_url": "",
        "single_iframe_url": "",
        "single_once_iframe_url": ""
    },
    "deployment_status": "deployed",
    "name":"test"
}
@pytest.fixture
def mock_asset_draft_response():
    return {
        "deployment_status": "draft",
        "deployment__links": {},
        "name": "test_asset",
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


def generate_mock_response(message_type):
    return {
        "status": "complete",
        "uid": "iEq4FGzZkLFKn33ZhkwEFi",
        "messages": {
            message_type: [
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
def mock_import_create_response():
    return generate_mock_response("created")


@pytest.fixture
def mock_import_update_response():
    return generate_mock_response("updated")


# For project initialization tests
@pytest.fixture
def project_name():
    return "test_project"


# For project initialization tests
@pytest.fixture
def expected_headers():
    return {
        "survey": [
            "type",
            "name",
            "label::English (en)",
            "hint::English (en)",
            "guidance_hint::English (en)",
            "required",
            "required_message::English (en)",
            "readonly",
            "relevant",
            "appearance",
            "default",
            "constraint",
            "constraint_message::English (en)",
            "calculation",
            "trigger",
            "choice_filter",
            "parameters",
            "repeat_count",
            "image::English (en)",
            "audio::English (en)",
            "video::English (en)",
            "note",
        ],
        "choices": [
            "list_name",
            "name",
            "label::English (en)",
            "image::English (en)",
        ],
        "settings": [
            "form_title",
            "form_id",
            "style",
            "version",
            "default_language",
            "allow_choice_duplicates",
            "instance_name",
        ],
    }


# For export tests
@pytest.fixture
def mock_export_mreq_response():
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


# For export tests
@pytest.fixture
def mock_export_wfc_response():
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


# For export tests
@pytest.fixture
def mock_export_file_content():
    return b"test,data\n1,2\n3,4"
