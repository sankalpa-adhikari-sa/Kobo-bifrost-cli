import os
from pathlib import Path
from typing import Any, Dict, Optional

import typer
from rich import print
from rich.prompt import Confirm
from typing_extensions import Annotated

from bifrost_cli.utils import (
    _make_request,
    _wait_for_completion,
    get_asset_id_and_xlsxform_path,
    get_credentials,
)

app = typer.Typer()


def export_data(
    asset_id: str, base_url: str, file_path: str, export_options: Dict[str, Any]
) -> None:
    """
    Exports the submission data

    Args:
        base_url (str): The base URL of the API.
        asset_id (str): The ID of the form.
        file_path (str): Local filepath to save the submission data.
        export_options (dict):
            Export configuration option for the data to download.
    """
    exports_url = f"{base_url}assets/{asset_id}/exports/"
    response = _make_request(
        method="POST",
        url=exports_url,
        data=export_options,
        params={"format": "json"},
    )
    if response.status_code == 400:
        print("[red]Somthing went Wrong! Try again....[/red]")
        return

    exp = response.json()["url"]

    data_url_res = _wait_for_completion(url=exp)

    if data_url_res is None:
        print("[red]Somthing went Wrong! Try again....[/red]")
        return
    data_res = _make_request(method="GET", url=data_url_res["result"])

    if data_res.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(data_res.content)
            print(
                f"[green]File downloaded successfully and saved to {file_path}.[/green]"
            )
    else:
        print(
            f"[red]Failed to download file. Status code: {data_res.status_code}[/red]"
        )


@app.command()
def csv(
    output_name: Annotated[str, typer.Option(help="Output file name.")],
    asset_id: Annotated[
        Optional[str],
        typer.Option(
            "--asset-id",
            help=(
                "The asset ID of the asset to export data."
                " Provide this or ensure it is saved."
            ),
        ),
    ] = None,
    download_path: Annotated[
        Optional[Path],
        typer.Option(help="Download path. Defaults to the current directory."),
    ] = None,
    separator: Annotated[
        str,
        typer.Option("-sep", "--separator", help="Group separator for data."),
    ] = "/",
    current_version: Annotated[
        bool,
        typer.Option("-c", "--current-version", help="Include data from all versions."),
    ] = True,
    gheaders: Annotated[
        bool,
        typer.Option("-gh", "--gheaders", help="Include group headers in the export."),
    ] = False,
    language: Annotated[
        str,
        typer.Option(
            "-lang",
            "--language",
            help="Language for the export: _default, _xml, or language code.",
        ),
    ] = "_default",
    no_media_url: Annotated[
        bool,
        typer.Option("-nmu", "--no-media-url", help="Include media URL in the export."),
    ] = True,
    multiple_select: Annotated[
        str,
        typer.Option(
            "-ms",
            "--multiple-select",
            help="Multiple select option: details, both, or summary.",
            case_sensitive=False,
        ),
    ] = "summary",
) -> None:
    """Export data as CSV."""
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
            f"[red]Error: No such directory: {download_path}. "
            "Please check the path and try again.[/red]"
        )
        return None
    file_path = os.path.join(download_path, f"{output_name}.csv")

    export_options = {
        "fields": [],
        "type": "csv",
        "fields_from_all_versions": current_version,
        "group_sep": separator,
        "hierarchy_in_labels": gheaders,
        "lang": language,
        "multiple_select": multiple_select,
        "include_media_url": no_media_url,
        "xls_types_as_text": False,
    }

    export_data(
        asset_id=asset_id,
        base_url=base_url,
        file_path=file_path,
        export_options=export_options,
    )


@app.command()
def xls(
    output_name: Annotated[str, typer.Option(help="Output file name.")],
    asset_id: Annotated[
        Optional[str],
        typer.Option(
            "--asset-id",
            help=(
                "The asset ID of the asset to export data. "
                "Provide this or ensure it is saved."
            ),
        ),
    ] = None,
    download_path: Annotated[
        Optional[Path],
        typer.Option(help="Download path. Defaults to the current directory."),
    ] = None,
    separator: Annotated[
        str,
        typer.Option("-sep", "--separator", help="Group separator for data."),
    ] = "/",
    current_version: Annotated[
        bool,
        typer.Option("-c", "--current-version", help="Include data from all versions."),
    ] = True,
    gheaders: Annotated[
        bool,
        typer.Option("-gh", "--gheaders", help="Include group headers in the export."),
    ] = False,
    language: Annotated[
        str,
        typer.Option(
            "-lang",
            "--language",
            help="Language for the export: _default, _xml, or language code.",
        ),
    ] = "_default",
    no_media_url: Annotated[
        bool,
        typer.Option("-nmu", "--no-media-url", help="Include media URL in the export."),
    ] = True,
    xtext: Annotated[
        bool,
        typer.Option("-xt", "--xtext", help="Store data and number response as text."),
    ] = False,
    multiple_select: Annotated[
        str,
        typer.Option(
            "-ms",
            "--multiple-select",
            help="Multiple select option: details, both, or summary.",
            case_sensitive=False,
        ),
    ] = "summary",
) -> None:
    """Export data as XLS."""
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
            f"[red]Error: No such directory: {download_path}. "
            "Please check the path and try again.[/red]"
        )
        return None
    file_path = os.path.join(download_path, f"{output_name}.xlsx")

    export_options = {
        "fields": [],
        "type": "xls",
        "fields_from_all_versions": current_version,
        "group_sep": separator,
        "hierarchy_in_labels": gheaders,
        "lang": language,
        "multiple_select": multiple_select,
        "include_media_url": no_media_url,
        "xls_types_as_text": xtext,
    }

    export_data(
        asset_id=asset_id,
        base_url=base_url,
        file_path=file_path,
        export_options=export_options,
    )


if __name__ == "__main__":
    app()
