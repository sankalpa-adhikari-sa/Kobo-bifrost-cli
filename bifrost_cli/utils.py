import requests
import keyring
from rich import print
import typer
from typing import Optional, Union
import time
import os
from pathlib import Path

SERVICE_NAME = "kobo-bifrost"


def get_credentials():
    """Retrieve credentials from the keyring."""
    api_key = keyring.get_password(SERVICE_NAME, "api_key")
    api_url = keyring.get_password(SERVICE_NAME, "api_url")

    if api_key and api_url:
        api_url = api_url if api_url.endswith("/") else f"${api_url}/"
        return api_key, api_url
    else:
        print(
            "❌ No credentials were found."
            "Use [blue]set-credentials[/blue] command to setup credentials."
        )
        raise typer.Abort()


def _make_request(method: str, url: str, **kwargs) -> requests.Response:
    api_key, _ = get_credentials()
    api_key = api_key
    headers = {"Authorization": f"Token {api_key}"}
    try:
        response = requests.request(
            method=method, url=url, headers=headers, **kwargs
        )
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"Error during making {method} request: {e}")


def _check_status(url: str) -> dict:
    return _make_request("GET", url=url).json()


def _wait_for_completion(url: str) -> Union[None, dict]:
    """
    Wait for a process to complete by polling a given URL.

    Args:
        url (str): The URL to poll for status updates.

    Returns:
        Union[None, Dict]: The final status response if completed,
        or None if an error occurs.
    """
    while True:
        status_response = _check_status(url)
        if status_response["status"] == "processing":
            print(
                "Status: still processing. Checking again in a few seconds..."
            )
            time.sleep(5)
        elif status_response["status"] == "complete":

            return status_response
        else:
            print("💥 Something went wrong!")
            break


def _import_form(
    url: str, data: dict, file_path: Optional[str] = None
) -> Optional[dict]:
    """
    Imports a form by sending a POST request with the XLS or XLSX file.

    Args:
        url (str): The URL to send the import request.
        data (dict): The data payload for the request.
        file_path (Optional[str]): The path to the XLS or XLSX file.

    Returns:
        Optional[Dict]: The response from the import process if successful,
        None otherwise.
    """
    if not file_path or not (
        file_path.lower().endswith(".xls")
        or file_path.lower().endswith(".xlsx")
    ):
        print(
            "Error: The file must be an .xls or .xlsx form. "
            "Please provide a valid file path."
        )
        return None

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}.")
        return None

    try:
        with open(file_path, "rb") as file:
            imported_xls_form = {"file": file}
            response = _make_request(
                "POST",
                url,
                data=data,
                files=imported_xls_form,
                params={"format": "json"},
            )

            if response is None:
                print(
                    "Error: No response received. "
                    "Please check your internet connection or the server."
                )
                return None

            if response.status_code == 201:
                response_data = response.json()
                current_form_import_url = response_data["url"]
                import_response = _wait_for_completion(current_form_import_url)
                return import_response
            else:
                print(
                    "Failed to start import. "
                    f"Status code: {response.status_code}"
                )
                print(response.text)
                return None
    except AttributeError:
        print(
            "Error: Unexpected response format or None received. "
            "Please check your network connection or the server."
        )
        return None
    except FileNotFoundError:
        print(f"Error: The file at {file_path} could not be found.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

    except FileNotFoundError:
        print(f"File not found: {file_path}. Please provide valid filepath.")
        return None


BIFROST_DIR = Path(".bifrost")
INFO_FILE = BIFROST_DIR / "info.txt"


def initialize_bifrost(xlsx_path: str = None):
    if not BIFROST_DIR.exists():
        BIFROST_DIR.mkdir(parents=True)

    if not INFO_FILE.exists():
        update_asset_info(asset_id=None, xlsx_path=xlsx_path)


def get_asset_id_and_xlsxform_path():
    if INFO_FILE.exists():
        with open(INFO_FILE, "r") as f:
            lines = f.readlines()
            asset_id = None
            xlsx_path = None
            download_path = None

            for line in lines:
                if line.startswith("Asset ID:"):
                    asset_id = line.strip().split(":")[1].strip()
                elif line.startswith("XlsForm Path:"):
                    xlsx_path = line.strip().split(":")[1].strip()
                elif line.startswith("Download Path:"):
                    download_path = line.strip().split(":")[1].strip()

            return asset_id, xlsx_path, download_path
    return None, None, None


def update_asset_info(
    asset_id: str = None, xlsx_path: str = None, download_path: str = None
) -> None:

    if not BIFROST_DIR.exists():
        BIFROST_DIR.mkdir(parents=True)

    lines = []
    if INFO_FILE.exists():
        with open(INFO_FILE, "r") as f:
            lines = f.readlines()

    asset_id_updated = False
    xlsx_path_updated = False
    download_path_updated = False

    for i, line in enumerate(lines):
        if line.startswith("Asset ID:"):
            if asset_id:
                lines[i] = f"Asset ID: {asset_id}\n"
                asset_id_updated = True
        elif line.startswith("XlsForm Path:"):
            if xlsx_path:
                lines[i] = f"XlsForm Path: {xlsx_path}\n"
                xlsx_path_updated = True
        elif line.startswith("Download Path:"):
            if download_path:
                lines[i] = f"Download Path: {download_path}\n"
                download_path_updated = True

    if not asset_id_updated and asset_id:
        lines.append(f"Asset ID: {asset_id}\n")
        print("Added Asset ID to info.txt.")

    if not xlsx_path_updated and xlsx_path:
        lines.append(f"XlsForm Path: {xlsx_path}\n")
        print("Added XlsForm Path to info.txt.")

    if not download_path_updated and download_path:
        lines.append(f"Download Path: {download_path}\n")
        print("Added Download Path to info.txt.")

    with open(INFO_FILE, "w") as f:
        f.writelines(lines)
        print("Updated info.txt successfully.")
