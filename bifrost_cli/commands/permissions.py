import typer
from rich import print
from typing_extensions import Annotated, Optional

from bifrost_cli.utils import (
    _make_request,
    get_asset_id_and_xlsxform_path,
    get_credentials,
)

app = typer.Typer()


def submission_without_auth(asset_id: str, base_url: str) -> None:
    """
    Enable data submission without any authentication.

    Args:
        base_url (str): The base URL of the API.
        asset_id (str): The ID of the form.
    """
    permission_url = f"{base_url}assets/{asset_id}/permission-assignments/"
    permission = {
        "user": "https://eu.kobotoolbox.org/api/v2/users/AnonymousUser/",
        "permission": "https://eu.kobotoolbox.org/api/v2/permissions/add_submissions/",
    }

    response = _make_request("POST", url=permission_url, data=permission)
    if response is not None and response.status_code == 201:
        print(
            "[green]✅ Successfully updated permission to submit data without auth.[/green]"
        )
    else:
        print("[red]💥 Failed to set permissions.[/red]")


def clone_asset_permission(asset_id: str, source_asset_id: str, base_url: str) -> None:
    """
    Clone the permissions (authorizations) from other asset.

    Args:
        asset_id (str): Asset id of project to which permission will be cloned
        source_asset_id (str):
            Asset id of project from which permission needs to be cloned
        base_url (str): The base URL of the API.


    """
    clone_permission_url = f"{base_url}assets/{asset_id}/permission-assignments/clone/"
    cloned_permission = {"clone_from": source_asset_id}
    response = _make_request("PATCH", url=clone_permission_url, data=cloned_permission)

    if response is not None and response.status_code == 200:

        print(
            f"[green]✅ Successfully cloned permission from \n source_asset_id: {source_asset_id}[/green]"
        )

    else:
        print(
            "[red]💥 Failed to clone permission."
            "Make Sure the source and target asset uid are valid.[/red]"
        )


@app.command()
def clone_permissions(
    source_asset_id: Annotated[
        str,
        typer.Option(
            "--from",
            help=("Asset id of project from which permission needs to be coloned"),
        ),
    ],
    target_asset_id: Annotated[
        str,
        typer.Option(
            "--to",
            help="Asset id of project to which permission will be cloned",
        ),
    ],
) -> None:
    """
    Clones permissions from source project to another target project.
    """
    _, base_url = get_credentials()
    if base_url is None:
        raise ValueError("Base URL is missing. Please provide valid credentials.")
    clone_asset_permission(
        asset_id=target_asset_id,
        source_asset_id=source_asset_id,
        base_url=base_url,
    )


# To do: Add other permissions and make --no-auth-sub flag to be optional.
@app.command()
def set_permissions(
    no_auth_sub: Annotated[
        bool,
        typer.Option(
            help="Allow submission without authentication.",
        ),
    ],
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
    Sets asset permissions.

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

    if no_auth_sub:
        submission_without_auth(asset_id=asset_id, base_url=base_url)


if __name__ == "__main__":
    app()
