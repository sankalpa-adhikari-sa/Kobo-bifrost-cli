from typing import Optional
from typing_extensions import Annotated
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..utils import (
    get_credentials,
    _make_request,
    get_asset_id_and_xlsxform_path,
)
from rich import print
import os

app = typer.Typer()


def get_asset(
    base_url: str, asset_id: str, file_path: str, asset_type: str
) -> None:
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
        task = progress.add_task(
            description="Fetching asset data...", start=False
        )

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
        str,
        typer.Option(
            "--asset-id",
            help="The asset ID of the asset to download. Provide this or ensure it is saved.",
        ),
    ] = None,
    download_path: Annotated[
        Optional[str],
        typer.Option(help="Download path. Defaults to the current directory."),
    ] = None,
) -> None:
    """Download Project Asset in XLS form

    Args:
        asset_id (str): The asset UID of the Project form.
        download_path (Optional[str]): The local directory path to save the downloaded asset. Defaults to the current directory.

    """
    _, base_url = get_credentials()

    if not asset_id or not download_path:
        saved_asset_id, _, saved_download_path = (
            get_asset_id_and_xlsxform_path()
        )
        if not asset_id:
            if not saved_asset_id:
                raise typer.BadParameter(
                    "Error: Missing option '--asset-id'. Provide it as an option or ensure it's saved."
                )
            asset_id = saved_asset_id
        if not download_path:
            download_path = saved_download_path or os.getcwd()

    if not os.path.exists(download_path):
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
        str,
        typer.Option(
            "--asset-id",
            help="The asset ID of the asset to download. Provide this or ensure it is saved.",
        ),
    ] = None,
    download_path: Annotated[
        Optional[str],
        typer.Option(help="Download path. Defaults to the current directory."),
    ] = None,
) -> None:
    """
    Download Project Asset in xml form.

    Args:
        asset_id (str): The asset UID of the Project form.
        download_path (Optional[str]): The local path to save the downloaded asset. Defaults to the current directory.
    """
    _, base_url = get_credentials()
    if not asset_id or not download_path:
        saved_asset_id, _, saved_download_path = (
            get_asset_id_and_xlsxform_path()
        )
        if not asset_id:
            if not saved_asset_id:
                raise typer.BadParameter(
                    "Error: Missing option '--asset-id'. Provide it as an option or ensure it's saved."
                )
            asset_id = saved_asset_id
        if not download_path:
            download_path = saved_download_path or os.getcwd()
    if not os.path.exists(download_path):
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
