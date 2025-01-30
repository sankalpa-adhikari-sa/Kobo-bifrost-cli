from pathlib import Path
from unittest.mock import MagicMock, patch

from bifrost_cli.commands.export import app as export_app


@patch("bifrost_cli.commands.export._make_request")
@patch("bifrost_cli.commands.export._wait_for_completion")
def test_export_success(
    mock_wait_for_completion,
    mock_make_request,
    runner,
    mock_keyring,
    mock_export_file_content,
    mock_export_mreq_response,
    mock_export_wfc_response,
    isolated_filesystem,
):

    mock_response1 = MagicMock()
    mock_response1.json.return_value = mock_export_mreq_response

    mock_response2 = MagicMock()
    mock_response2.status_code = 200
    mock_response2.content = mock_export_file_content

    mock_make_request.side_effect = [mock_response1, mock_response2]

    mock_wait_for_completion.return_value = mock_export_wfc_response

    mock_keyring["get_password"].side_effect = {
        ("kobo-bifrost", "api_key"): "previous-api-key",
        ("kobo-bifrost", "api_url"): "previous-api-url",
    }.get

    output_file = Path(isolated_filesystem) / "my_file.csv"

    result = runner.invoke(
        export_app,
        [
            "csv",
            "--asset-id",
            "valid_asset_id",
            "--output-name",
            "my_file",
            "--download-path",
            isolated_filesystem,
        ],
    )

    assert result.exit_code == 0
    assert "File downloaded successfully and saved to" in result.stdout.replace(
        "\n", ""
    )
    with open(output_file, "rb") as f:
        assert f.read() == mock_export_file_content

    assert mock_make_request.call_count == 2
    assert mock_wait_for_completion.call_count == 1
