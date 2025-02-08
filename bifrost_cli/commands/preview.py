import typer
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from typing_extensions import Annotated, Dict, Optional, cast

from bifrost_cli.utils import (
    _make_request,
    get_asset_id_and_xlsxform_path,
    get_credentials,
    update_asset_info,
)

app = typer.Typer()


def preview_asset_snapshot(
    asset_id: str,
    base_url: str,
) -> Optional[Dict]:
    """
    Updates and asset(form).

    Args:
        base_url (str): The base URL of the API.
        asset_id (str): The ID of the form.
    """
    import_url = f"{base_url}asset_snapshots/"
    form_asset_url = f"{base_url}assets/{asset_id}/"
    data = {
        "asset": form_asset_url,
    }

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description="Fetching asset snapshots...", start=False)
        progress.start_task(task)
        response = _make_request(method="POST", url=import_url, data=data)
        progress.update(task, completed=100)

    if response is not None and response.status_code == 201:
        print("[green]✅ Successfully fetched asset snapshots[/green]")
        return cast(Dict, response.json())
    else:
        print("[red]❌ Failed to fetch asset snapshot.[/red]")
        print("[red]Survey form may be empty or untitled or invalid asset ID.[/red]")
        return None


@app.command()
def preview(
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
    Preview asset snapshots.
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
    res = preview_asset_snapshot(asset_id=asset_id, base_url=base_url)
    if res:
        typer.launch(res["enketopreviewlink"])
        table = Table(title="Deployment Details")
        table.add_column("SN", justify="right", overflow="fold")
        table.add_column("Asset ID", justify="right", overflow="fold")
        table.add_column("Form Title", justify="right", overflow="fold")
        table.add_column("Snapshot Preview link", justify="right", overflow="fold")
        table.add_row(
            "1",
            asset_id,
            res["source"]["settings"]["form_title"],
            res["enketopreviewlink"],
        )
        print(table)
    else:
        return
    update_asset_info(asset_id=asset_id)
