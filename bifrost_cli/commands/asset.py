import os
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from typing_extensions import Annotated

from bifrost_cli.utils import (
    _make_request,
    get_asset_id_and_xlsxform_path,
    get_credentials,
)

app = typer.Typer()


def get_asset(base_url: str, asset_id: str, file_path: str, asset_type: str) -> None:
    """
    Downloads an asset from a specified URL and saves it to a file.

    Args:
        base_url (str): The base URL of the API.
        asset_id (str): The ID of the form.
        file_path (str): The local file path to save the downloaded asset.
        asset_type (str): The type of asset to download.


    """
    asset_download_url = f"{base_url}assets/{asset_id}.{asset_type}/"
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description="Fetching asset data...", start=False)

        progress.start_task(task)
        response = _make_request(
            method="GET", url=asset_download_url, params={"format": "json"}
        )
        progress.update(task, completed=100)
    if response is not None and response.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"✅ File downloaded successfully and saved to {file_path}.")
    else:
        print("💥 Failed to download file.")


@app.command("xls")
def asset_xls(
    asset_id: Annotated[
        Optional[str],
        typer.Option(
            "--asset-id",
            help=(
                "The asset ID of the asset to download."
                "Provide this or ensure it is saved."
            ),
        ),
    ] = None,
    download_path: Annotated[
        Optional[Path],
        typer.Option(help="Download path. Defaults to the current directory."),
    ] = None,
) -> None:
    """Download Project Asset in XLS form

    Args:
        asset_id (str): The asset UID of the Project form.
        download_path (Optional[Path]):
            The local directory path to save the downloaded asset.
            Defaults to the current directory.

    """
    _, base_url = get_credentials()
    if base_url is None:
        raise ValueError("Base URL is missing. Please provide valid credentials.")

    if not asset_id or not download_path:
        saved_asset_id, _, saved_download_path = get_asset_id_and_xlsxform_path()
        if not asset_id:
            asset_id = saved_asset_id
        if not download_path:
            download_path = Path(saved_download_path) if saved_download_path else None

    if not asset_id:
        raise typer.BadParameter(
            "Error: Missing option '--asset-id'."
            "Provide it as an option or ensure it's saved."
        )
    if not download_path:
        use_cwd = Confirm.ask(
            "No download path specified. Do you want to use the current directory?"
        )
        if use_cwd:
            download_path = Path.cwd()
        else:
            print("Download path not specified. Exiting.")
            return
    download_path = Path(download_path).resolve()
    if not download_path.exists():
        print(
            f"Error: No such directory: {download_path}. "
            "Please check the path and try again."
        )
        return None
    file_path = os.path.join(download_path, f"{asset_id}.xlsx")
    get_asset(
        base_url=base_url,
        asset_id=asset_id,
        file_path=file_path,
        asset_type="xls",
    )


@app.command("xml")
def asset_xml(
    asset_id: Annotated[
        Optional[str],
        typer.Option(
            "--asset-id",
            help=(
                "The asset ID of the asset to download."
                "Provide this or ensure it is saved."
            ),
        ),
    ] = None,
    download_path: Annotated[
        Optional[Path],
        typer.Option(help="Download path. Defaults to the current directory."),
    ] = None,
) -> None:
    """
    Download Project Asset in xml form.

    Args:
        asset_id (str): The asset UID of the Project form.
        download_path (Optional[Path]):
            The local path to save the downloaded asset.
            Defaults to the current directory.
    """
    _, base_url = get_credentials()
    if base_url is None:
        raise ValueError("Base URL is missing. Please provide valid credentials.")

    if not asset_id or not download_path:
        saved_asset_id, _, saved_download_path = get_asset_id_and_xlsxform_path()
        if not asset_id:
            asset_id = saved_asset_id
        if not download_path:
            download_path = Path(saved_download_path) if saved_download_path else None

    if not asset_id:
        raise typer.BadParameter(
            "Error: Missing option '--asset-id'."
            "Provide it as an option or ensure it's saved."
        )
    if not download_path:
        use_cwd = Confirm.ask(
            "No download path specified. Do you want to use the current directory?"
        )
        if use_cwd:
            download_path = Path.cwd()
        else:
            print("Download path not specified. Exiting.")
            return
    download_path = Path(download_path).resolve()
    if not download_path.exists():
        print(
            f"Error: No such directory: {download_path}. "
            "Please check the path and try again."
        )
        return None
    file_path = os.path.join(download_path, f"{asset_id}.xml")

    get_asset(
        base_url=base_url,
        asset_id=asset_id,
        file_path=file_path,
        asset_type="xml",
    )


if __name__ == "__main__":
    app()
