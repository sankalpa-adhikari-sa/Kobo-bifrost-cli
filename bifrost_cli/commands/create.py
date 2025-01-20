from typing_extensions import Annotated
import typer
from rich.console import Console
from rich.table import Table

from rich.progress import Progress, SpinnerColumn, TextColumn
from ..utils import (
    get_credentials,
    _import_form,
    update_asset_info,
    get_asset_id_and_xlsxform_path,
)
from rich import print

from bifrost_cli.commands.deploy import deploy_form
from typing import Union

app = typer.Typer()


def create_form(file_path: str, base_url: str) -> Union[None, str]:
    """
    Creates a new project asset(form)

    Args:
        file_path (str): The path to the project form in XLS or  XLSX.
        base_url (str): The base URL to create import url.

    Returns:
        Union[None, str]: Asset UID if completed or returns None if an error occurs.

    """
    console = Console()
    import_url = base_url + "imports/"
    data = {"library": "false"}
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(
            description="Starting Form Creation Procedure...", start=False
        )
        progress.start_task(task)
        response = _import_form(url=import_url, data=data, file_path=file_path)
        progress.update(task, completed=100)

    if response is not None:

        res = response["messages"]["created"][0]
        table = Table(title="\nInformation of created asset")
        table.add_column("SN", justify="right", no_wrap=True)
        table.add_column("AssetID", justify="right", overflow="fold")
        table.add_column("Owner", justify="right", overflow="fold")
        table.add_column("creation", justify="right", overflow="fold")
        table.add_row("1", res["uid"], res["owner__username"], "successful")
        console = Console()
        console.print(table)
        return res["uid"]
    else:
        print("Failed to create form.")


@app.command()
def create(
    filepath: Annotated[
        str,
        typer.Option(
            "--filepath",
            help="The path to the XLSForm file to update. Provide this or ensure it is saved.",
        ),
    ] = None,
    deploy: Annotated[
        bool,
        typer.Option(
            "-d", "--deploy", help="Deploy the project after creation."
        ),
    ] = False,
):
    """
    Creates a new asset(form) in Kobotoolbox.
    """
    _, base_url = get_credentials()
    if not filepath:
        _, saved_filepath, _ = get_asset_id_and_xlsxform_path()

        if not filepath:
            if not saved_filepath:
                raise typer.BadParameter(
                    "Error: Missing option '--filepath'. Provide it as an option or ensure it's saved."
                )
            filepath = saved_filepath
    asset_id = create_form(filepath, base_url)
    if asset_id and filepath:
        update_asset_info(asset_id=asset_id, xlsx_path=filepath)

    if deploy and asset_id:
        deploy_form(asset_id=asset_id, base_url=base_url)


if __name__ == "__main__":
    app()
