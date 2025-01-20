from typing_extensions import Annotated
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..utils import (
    get_credentials,
    _make_request,
    get_asset_id_and_xlsxform_path,
    update_asset_info,
)
from rich import print
from rich.table import Table

app = typer.Typer()


def view_asset_snapshot(
    asset_id: str,
    base_url: str,
) -> None:
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
        task = progress.add_task(
            description="Fetching asset snapshots...", start=False
        )
        progress.start_task(task)
        response = _make_request(method="POST", url=import_url, data=data)
        progress.update(task, completed=100)

    if response is not None:

        print("✅ Successfully fetched asset snaphsots")
        return response.json()
    else:
        print("❌ Failed to fetch asset snapshot.")
        print("Survey form may be empty or untitled or invalid asset ID.")
        return None


@app.command()
def view(
    asset_id: Annotated[
        str,
        typer.Option(
            "--asset-id",
            help="The asset ID of the form to update. Provide this or ensure it is saved.",
        ),
    ] = None
):
    """
    View asset snapshots.
    """
    _, base_url = get_credentials()
    if not asset_id:
        saved_asset_id, _, _ = get_asset_id_and_xlsxform_path()
        if not asset_id:
            if not saved_asset_id:
                raise typer.BadParameter(
                    "Error: Missing option '--asset-id'. Provide it as an option or ensure it's saved."
                )
            asset_id = saved_asset_id
    update_asset_info(asset_id=asset_id)

    res = view_asset_snapshot(asset_id=asset_id, base_url=base_url)
    if res:
        typer.launch(res["enketopreviewlink"])
        table = Table(title="Deployment Details")
        table.add_column("SN", justify="right", overflow="fold")
        table.add_column("Asset ID", justify="right", overflow="fold")
        table.add_column("Form Title", justify="right", overflow="fold")
        table.add_column(
            "Snapshot Preview link", justify="right", overflow="fold"
        )
        table.add_row(
            "1",
            asset_id,
            res["source"]["settings"]["form_title"],
            res["enketopreviewlink"],
        )
        print(table)
