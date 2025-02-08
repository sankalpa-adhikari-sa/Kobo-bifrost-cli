import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, cast

import keyring
import requests
import typer
from rich import print

SERVICE_NAME = "kobo-bifrost"


def get_credentials() -> Tuple[Optional[str], Optional[str]]:
    """Retrieve credentials from the keyring."""
    api_key = keyring.get_password(SERVICE_NAME, "api_key")
    api_url = keyring.get_password(SERVICE_NAME, "api_url")

    if api_key and api_url:
        api_url = api_url if api_url.endswith("/") else f"${api_url}/"
        return api_key, api_url
    else:
        print(
            "[red]❌ No credentials were found.[/red]"
            "Use [blue]set-credentials[/blue] command to setup credentials."
        )
        raise typer.Abort()


def _make_request(method: str, url: str, **kwargs: Any) -> requests.Response:
    api_key, _ = get_credentials()
    headers = {"Authorization": f"Token {api_key}"}
    try:
        response = requests.request(method=method, url=url, headers=headers, **kwargs)

        return response
    except requests.RequestException as e:
        print(f"[red]Error during making {method} request: {e} [red]")
        raise


def _check_status(url: str) -> Optional[Dict[str, Any]]:
    response = _make_request("GET", url=url)
    if response:
        return cast(Dict[str, Any], response.json())
    else:
        raise ValueError(f"Failed to retrieve a valid response from {url}")


def _wait_for_completion(url: str, timeout: Optional[int] = 180) -> Optional[Dict]:
    """
    Wait for a process to complete by polling a given URL.

    Args:
        url (str): The URL to poll for status updates.
        timeout (Optional[int]): The maximum time (in seconds) to wait for completion. Defaults to 300 seconds.

    Returns:
        Optional[Dict]: The final status response if completed,
        or None if an error occurs or timeout is reached.
    """
    start_time = time.time()

    while True:
        try:
            # Call to the function that checks the status
            status_response = _check_status(url)
            if status_response is None:
                print("[red]❌ Error: Received None as status response.[/red]")
                return None
        except Exception:
            print("[red]❌ Error checking status.[/red]")
            return None

        if "status" not in status_response:
            print("[red]❌ Invalid response format. Missing 'status' field.[/red]")
            return None

        if status_response["status"] == "processing":
            print("⏳ Status: still processing. Checking again in 5 seconds...")
            time.sleep(5)

            # Check if the timeout has been reached
            if timeout is not None and (time.time() - start_time) > timeout:
                print(f"⏰ Timeout reached after {timeout} seconds.")
                return None

        elif status_response["status"] == "complete":

            return status_response

        else:
            print(f"💥 Unexpected status: {status_response['status']}")
            return None


def _import_form(
    url: str, data: dict, file_path: Optional[Path] = None
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
    if not file_path or file_path.suffix.lower() not in [".xls", ".xlsx"]:
        print(
            "[red]Error: The file must be an .xls or .xlsx form. "
            "Please provide a valid file path.[/red]"
        )
        return None

    if not file_path.exists():
        print(f"[red]Error: File not found at {file_path}. [/red]")
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
            if response.status_code == 201:
                response_data = response.json()
                current_form_import_url = response_data["url"]
                import_response = _wait_for_completion(current_form_import_url)
                return import_response
            else:
                print(
                    "[red]Failed to start import. "
                    f"Status code: {response.status_code} [/red]"
                )
                print(response.text)
                return None
    except AttributeError:
        print(
            "[red]Error: Unexpected response format or None received. "
            "Please check your network connection or the server.[/red]"
        )
        return None
    except FileNotFoundError:
        print(f"[red]Error: The file at {file_path} could not be found.[/red]")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def find_bifrost_dir(start_dir: Path = Path(".")) -> Optional[Path]:
    """
    Traverses up the directory tree to find the .bifrost directory.
    Args:
        start_dir (Path): The directory to start the search from. Defaults to the current directory.

    Returns:
        Optional[Path]: The path to the .bifrost directory if found, otherwise None.

    """
    current_dir = start_dir.resolve()
    while current_dir != current_dir.parent:
        bifrost_dir = current_dir / ".bifrost"
        if bifrost_dir.exists() and bifrost_dir.is_dir():
            return bifrost_dir
        current_dir = current_dir.parent
    return None


def initialize_bifrost(
    xlsx_path: Optional[Path] = None, bifrost_dir: Optional[Path] = None
) -> None:
    """
    Initialize the .bifrost directory in the specified directory.
    """
    BIFROST_DIR = bifrost_dir or Path(".bifrost")
    INFO_FILE = BIFROST_DIR / "info.txt"

    if not BIFROST_DIR.exists():
        BIFROST_DIR.mkdir(parents=True)

    if not INFO_FILE.exists():
        update_asset_info(asset_id=None, xlsx_path=xlsx_path, info_file=INFO_FILE)


def get_asset_id_and_xlsxform_path() -> (
    Tuple[Optional[str], Optional[str], Optional[str]]
):
    """
    Retrieve the Asset ID, XlsxForm Path, and Download Path from the info.txt file.
    """
    BIFROST_DIR = find_bifrost_dir() or Path(".bifrost")
    INFO_FILE = BIFROST_DIR / "info.txt"

    if INFO_FILE.exists():
        with open(INFO_FILE, "r") as f:
            lines = f.readlines()
            asset_id = None
            xlsx_path = None
            download_path = None

            for line in lines:
                if line.startswith("Asset ID="):
                    asset_id = line.strip().split("=")[1].strip()
                elif line.startswith("XlsForm Path="):
                    xlsx_path = line.split("=", 1)[1].strip()
                elif line.startswith("Download Path="):
                    download_path = line.split("=", 1)[1].strip()

            return asset_id, xlsx_path, download_path
    return None, None, None


def update_asset_info(
    asset_id: Optional[str] = None,
    xlsx_path: Optional[Path] = None,
    download_path: Optional[Path] = None,
    info_file: Optional[Path] = None,
) -> None:
    """
    Update the asset information in the specified info file.
    """
    if not info_file:
        BIFROST_DIR = find_bifrost_dir() or Path(".bifrost")
        INFO_FILE = BIFROST_DIR / "info.txt"
    else:
        INFO_FILE = info_file
    if not INFO_FILE.parent.exists():
        INFO_FILE.parent.mkdir(parents=True)
    lines = []
    if INFO_FILE.exists():
        with open(INFO_FILE, "r") as f:
            lines = f.readlines()

    asset_id_updated = False
    xlsx_path_updated = False
    download_path_updated = False

    for i, line in enumerate(lines):
        if line.startswith("Asset ID="):
            if asset_id:
                lines[i] = f"Asset ID= {asset_id}\n"
                asset_id_updated = True
        elif line.startswith("XlsForm Path="):
            if xlsx_path:
                lines[i] = f"XlsForm Path= {xlsx_path}\n"
                xlsx_path_updated = True
        elif line.startswith("Download Path="):
            if download_path:
                lines[i] = f"Download Path= {download_path}\n"
                download_path_updated = True

    if not asset_id_updated and asset_id:
        lines.append(f"Asset ID= {asset_id}\n")

    if not xlsx_path_updated and xlsx_path:
        lines.append(f"XlsForm Path= {xlsx_path}\n")

    if not download_path_updated and download_path:
        lines.append(f"Download Path= {download_path}\n")

    with open(INFO_FILE, "w") as f:
        f.writelines(lines)
        print("[green]Updated info.txt successfully.[/green]")
