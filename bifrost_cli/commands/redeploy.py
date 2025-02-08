import typer
from rich import print
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from typing_extensions import Annotated, Optional

from bifrost_cli.utils import (
    _make_request,
    get_asset_id_and_xlsxform_path,
    get_credentials,
)

app = typer.Typer()


def redeploy_form(asset_id: str, base_url: str) -> None:
    """
    Redeploy the asset(form).
    Args:
        base_url (str): The base URL of the API.
        asset_id (str): The ID of the form.
    """
    console = Console()
    form_asset_url = f"{base_url}assets/{asset_id}/"
    deployment_url = f"{base_url}assets/{asset_id}/deployment/"
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(
            description="Starting form Re-deployment...", start=False
        )

        progress.start_task(task)
        response = _make_request("GET", form_asset_url, params={"format": "json"})
        progress.update(task, completed=100)

    if response.status_code != 200:
        print("[red]Error: The form you are trying to redeploy may not exist.[/red]")
        return
    version_to_deploy = response.json()["version_id"]

    deployment_data = {"version_id": version_to_deploy, "active": True}

    response = _make_request(
        "PATCH",
        deployment_url,
        data=deployment_data,
        params={"format": "json"},
    )

    if response.status_code == 200:
        print("[green]✅ Successfully Re-deployed form[/green]")
        res = response.json()

        table = Table(title="Re-deployment Details")
        table.add_column("SN", justify="right", overflow="fold")
        table.add_column("Asset ID", justify="right", overflow="fold")
        table.add_column("Deployment Status", justify="right", overflow="fold")
        table.add_column("v.SN", justify="right", overflow="fold")
        table.add_column("v.ID", justify="right", overflow="fold")
        table.add_column("Deployment Link", justify="right", overflow="fold")
        table.add_column("Submission Count", justify="right", overflow="fold")
        table.add_row(
            "1",
            asset_id,
            res["asset"]["deployment_status"],
            f"{res['asset']['version_count']}",
            res["asset"]["deployed_version_id"],
            res["asset"]["deployment__links"]["url"],
            f"{res['asset']['deployment__submission_count']}",
        )

        console.print(table)
    elif response.status_code == 405:
        print("[red]Error: The form cannot be redeployed.[/red]")
        print(
            "[red]Please check the deployment status of the form and ensure it is deployed before attempting to redeploy.[/red]"
        )
    else:
        print("[red]Something went wrong![/red]")


@app.command()
def redeploy(
    asset_id: Annotated[
        Optional[str],
        typer.Option(
            "--asset-id",
            help=(
                "The asset ID of the form to update."
                " Provide this or ensure it is saved."
            ),
        ),
    ] = None,
) -> None:
    """
    Redeploys a specified asset(form).
    """
    _, base_url = get_credentials()
    if base_url is None:
        raise ValueError("Base URL is missing. Please provide valid credentials.")
    if not asset_id:
        asset_id, _, _ = get_asset_id_and_xlsxform_path()
        if not asset_id:
            raise typer.BadParameter(
                "Missing argument 'ASSET_ID'."
                " Provide it as an argument or ensure it's saved."
            )
    redeploy_form(asset_id, base_url)


if __name__ == "__main__":
    app()
