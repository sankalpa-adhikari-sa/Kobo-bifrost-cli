import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..utils import get_credentials, _make_request

app = typer.Typer()


@app.command()
def list_assets() -> None:
    """Lists all assets(forms) with basic information."""
    console = Console()
    _, base_url = get_credentials()
    asset_url = f"{base_url}assets/"

    def determine_modification_status(deployed_version_id, version_id):
        if deployed_version_id is None:
            return "-"
        return "No" if version_id == deployed_version_id else "Yes"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(
            description="Fetching asset data...", start=False
        )

        progress.start_task(task)
        response = _make_request("GET", asset_url, params={"format": "json"})
        progress.update(task, completed=100)

    if response is not None and response.status_code == 200:
        table = Table(title="\nList of Assets")
        table.add_column("SN", justify="right", no_wrap=True)
        table.add_column("Project name", overflow="fold")
        table.add_column("AssetID", justify="right", overflow="fold")
        table.add_column("Deployment status", justify="right")
        table.add_column("Has Undeployed Update ?", justify="right")
        table.add_column("Submission Count", justify="right")

        for index, asset in enumerate(response.json()["results"]):
            modification_status = determine_modification_status(
                asset.get("deployed_version_id"), asset.get("version_id")
            )
            table.add_row(
                f"{index+1}",
                asset["name"],
                asset["uid"],
                asset["deployment_status"],
                modification_status,
                f"{asset['deployment__submission_count']}",
            )
        console.print(table)
    else:
        console.print("[bold red]Failed to fetch asset data.[/bold red]")


if __name__ == "__main__":
    app()
