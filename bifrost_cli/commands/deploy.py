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


def deploy_form(asset_id: str, base_url: str) -> None:
    """
    Deploys a specified form.

    Args:
        base_url (str): The base URL of the API.
        asset_id (str): The ID of the form.
    """

    deployment_url = f"{base_url}assets/{asset_id}/deployment/"
    deployment_data = {"active": True}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(
            description="Starting Form deployment Procedure...", start=False
        )
        progress.start_task(task)
        response = _make_request(
            "POST",
            deployment_url,
            data=deployment_data,
            params={"format": "json"},
        )

        progress.update(task, completed=100)
        if response.status_code == 200:
            res = response.json()

            table = Table(title="\nDeployment Details")
            table.add_column("SN", justify="right", overflow="fold")
            table.add_column("Asset ID", justify="right", overflow="fold")
            table.add_column("Deployment Status", justify="right", overflow="fold")
            table.add_column("Deployment Link", justify="right", overflow="fold")
            table.add_row(
                "1",
                asset_id,
                res["asset"]["deployment_status"],
                res["asset"]["deployment__links"]["url"],
            )
            console = Console()
            console.print(table)
            print("[green]✅ Successfully Deployed form[/green]")
        else:
            print(
                "[red]Error: The form you are trying to deploy may not exist or \n"
                "The form cannot be deployed as it may already be deployed.[/red]"
            )
            print(
                "[red]Please check the form's deployment status and "
                "Ensure it hasn't been deployed before proceeding.[/red]"
            )


@app.command()
def deploy(
    asset_id: Annotated[
        Optional[str],
        typer.Option(
            "--asset-id",
            help=(
                "The asset ID of the form to update."
                "Provide this or ensure it is saved."
            ),
        ),
    ] = None,
) -> None:
    """
    Deploy an specified asset(form).
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

    deploy_form(asset_id, base_url)


if __name__ == "__main__":
    app()
