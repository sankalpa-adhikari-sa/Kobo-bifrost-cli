import typer
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from typing_extensions import Annotated

from bifrost_cli.utils import _make_request, get_credentials

app = typer.Typer()


def delete_form(asset_id: str, base_url: str) -> None:
    """
    Deletes the specified forms/asset.

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
            description="Starting Form Deletion Procedure...", start=False
        )
        progress.start_task(task)
        res = _make_request("DELETE", form_asset_url)

        progress.update(task, completed=100)

    if res is not None and res.status_code == 200:

        print(f"✅ Succssfully Deleted Form {asset_id}")
    else:
        print("💥 Failed to Delete Form")


@app.command()
def delete(
    asset_id: Annotated[
        str,
        typer.Option(
            "--asset-id",
            help="The asset ID of the form to delete.",
        ),
    ],
) -> None:
    """
    Deletes an asset(form).
    """
    _, base_url = get_credentials()
    if base_url is None:
        raise ValueError("Base URL is missing. Please provide valid credentials.")
    if not Confirm.ask(
        "Do you want to delete the project?\n"
        "[red]This action will delete all associated data and files.[/red]"
    ):
        print("[bold red]Aborting project Deletion.[/bold red]")
        raise typer.Abort()
    delete_form(asset_id=asset_id, base_url=base_url)


if __name__ == "__main__":
    app()
