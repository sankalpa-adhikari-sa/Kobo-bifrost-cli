from pathlib import Path

import typer
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Annotated, Optional, cast

from bifrost_cli.commands.deploy import deploy_form
from bifrost_cli.commands.preview import preview_asset_snapshot
from bifrost_cli.commands.redeploy import redeploy_form
from bifrost_cli.utils import (
    _import_form,
    get_asset_id_and_xlsxform_path,
    get_credentials,
    update_asset_info,
)

app = typer.Typer()


def update_form(
    asset_id: str,
    base_url: str,
    file_path: Path,
) -> Optional[str]:
    """
    Updates and asset(form).

    Args:
        base_url (str): The base URL of the API.
        asset_id (str): The ID of the form.
        file_path (str): The local path of the asset XLS form.
    """
    import_url = f"{base_url}imports/"
    form_asset_url = f"{base_url}assets/{asset_id}/"
    data = {
        "library": "false",
        "destination": form_asset_url,
        "assetUid": asset_id,
    }

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(
            description="Starting Form Update procedure...", start=False
        )
        progress.start_task(task)
        response = _import_form(url=import_url, data=data, file_path=file_path)
        progress.update(task, completed=100)

    if response is not None:
        print(
            "[green]✅ Successfully updated form "
            f"{response['messages']['updated'][0]['uid']}[/green]"
        )
        return cast(str, response["messages"]["updated"][0]["uid"])
    else:
        print("[red] ❌ Failed to update form.[/red]")
        return None


@app.command()
def update(
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
    filepath: Annotated[
        Optional[Path],
        typer.Option(
            "--filepath",
            help=(
                "The path to the XLSForm file to update."
                " Provide this or ensure it is saved."
            ),
        ),
    ] = None,
    deploy: Annotated[
        bool,
        typer.Option("-d", "--deploy", help="Deploy the project after creation."),
    ] = False,
    redeploy: Annotated[
        bool,
        typer.Option("-rd", "--redeploy", help="Redeploy the project after creation."),
    ] = False,
    preview_snapshots: Annotated[
        bool,
        typer.Option(
            "-ps",
            "--preview-snapshots",
            help="Preview snapshot of the updated asset.",
        ),
    ] = False,
) -> None:
    """Updates a specified existing asset(form)."""
    if deploy and redeploy:
        raise typer.BadParameter(
            "Error: You cannot specify both '--deploy, -d' and '--redeploy, -rd' options at the same time."
        )
    _, base_url = get_credentials()
    if base_url is None:
        raise ValueError("Base URL is missing. Please provide valid credentials.")
    if not asset_id or not filepath:
        saved_asset_id, saved_filepath, _ = get_asset_id_and_xlsxform_path()
        if not asset_id:
            asset_id = asset_id or saved_asset_id
        if not filepath:
            filepath = Path(saved_filepath) if saved_filepath else None

    if not asset_id:
        raise typer.BadParameter(
            "Error: Missing option '--asset-id'. Provide it as an option or ensure it's saved."
        )
    if not filepath:
        raise typer.BadParameter(
            "Error: Missing option '--filepath'. Provide it as an option or ensure it's saved."
        )
    # if isinstance(filepath, str):
    #     filepath = Path(filepath)

    res_uid = update_form(asset_id=asset_id, file_path=filepath, base_url=base_url)
    update_asset_info(asset_id=asset_id, xlsx_path=filepath)

    if res_uid is not None:
        if deploy:
            deploy_form(asset_id=res_uid, base_url=base_url)
        if redeploy:
            redeploy_form(asset_id=res_uid, base_url=base_url)
        if preview_snapshots:
            res_snap = preview_asset_snapshot(asset_id=res_uid, base_url=base_url)
            if res_snap:
                typer.launch(res_snap["enketopreviewlink"])


if __name__ == "__main__":
    app()
