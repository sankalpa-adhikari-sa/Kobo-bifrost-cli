import typer
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from typing_extensions import Annotated, Optional

from bifrost_cli.utils import (
    _make_request,
    get_asset_id_and_xlsxform_path,
    get_credentials,
    update_asset_info,
)

app = typer.Typer()


def get_deployment_links(
    asset_id: str,
    base_url: str,
) -> None:
    """
    Updates and asset(form).

    Args:
        base_url (str): The base URL of the API.
        asset_id (str): The ID of the form.
    """
    form_asset_url = f"{base_url}assets/{asset_id}/"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(
            description="Fetching asset deployment links...", start=False
        )
        progress.start_task(task)
        response = _make_request(
            method="GET", url=form_asset_url, params={"format": "json"}
        )
        progress.update(task, completed=100)

    if response.status_code == 200:
        res = response.json()
        if len(res["deployment__links"]) > 0:
            print(
                "✅ [bold green]Successfully fetched asset deployment links[/bold green]"
            )
            table = Table(title=f'Deployment Links - {asset_id} | {res["name"]}')
            table.add_column("SN", justify="right", overflow="fold")
            table.add_column("URL type", justify="right", overflow="fold")
            table.add_column("Url", justify="right", overflow="fold")
            table.add_row(
                "1",
                "Deployment Link",
                res["deployment__links"]["url"],
            )
            print(table)
        else:
            print(
                "❌ [bold red]No deployment links found. The asset might not have been deployed yet.[/bold red]"
            )
    else:
        print("❌ Failed to fetch asset.")


@app.command()
def deployment_links(
    asset_id: Annotated[
        Optional[str],
        typer.Option(
            "--asset-id",
            help=(
                "The asset ID of the form to update. "
                "Provide this or ensure it is saved."
            ),
        ),
    ] = None,
) -> None:
    """
    Fetch asset deployment links.
    """
    _, base_url = get_credentials()
    if base_url is None:
        raise ValueError("Base URL is missing. Please provide valid credentials.")
    if not asset_id:
        saved_asset_id, _, _ = get_asset_id_and_xlsxform_path()

        if not saved_asset_id:
            raise typer.BadParameter(
                "Error: Missing option '--asset-id'."
                " Provide it as an option or ensure it's saved."
            )
        asset_id = saved_asset_id

    assert asset_id is not None
    get_deployment_links(asset_id=asset_id, base_url=base_url)
    update_asset_info(asset_id=asset_id)
