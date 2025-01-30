import typer
from rich import print
from typing_extensions import Annotated

from bifrost_cli.utils import _make_request, get_credentials

app = typer.Typer()


def submission_without_auth(asset_id: str, base_url: str) -> None:
    """
    Enable data submission without any authentication.

    Args:
        base_url (str): The base URL of the API.
        asset_id (str): The ID of the form.
    """
    premission_url = f"{base_url}assets/{asset_id}/permission-assignments/"
    premission = {
        "user": "https://eu.kobotoolbox.org/api/v2/users/AnonymousUser/",
        "permission": "https://eu.kobotoolbox.org/api/v2/permissions/add_submissions/",
    }

    response = _make_request("POST", url=premission_url, data=premission)
    if response is not None and response.status_code == 201:
        print("✅ Successfuly updated premission to submit data without auth.")
    else:
        print("💥 Failed to set permissions.")


def clone_asset_premission(asset_id: str, source_asset_id: str, base_url: str) -> None:
    """
    Clone the permissions (authorizations) from other asset.

    Args:
        asset_id (str): Asset id of project to which permission will be coloned
        source_asset_id (str):
            Asset id of project from which permission needs to be coloned
        base_url (str): The base URL of the API.


    """
    clone_premission_url = f"{base_url}assets/{asset_id}/permission-assignments/clone/"
    cloned_premissions = {"clone_from": source_asset_id}
    response = _make_request("PATCH", url=clone_premission_url, data=cloned_premissions)

    if response is not None and response.status_code == 200:

        print(
            f"✅ Successfuly cloned premission from \n source_asset_id: {source_asset_id}"
        )

    else:
        print(
            "💥 Failed to clone premission."
            "Make Sure the source and target asset uid are valid."
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
            help="Asset id of project to which permission will be coloned",
        ),
    ],
) -> None:
    """
    Clones permissions from source project to another target project.
    """
    _, base_url = get_credentials()
    if base_url is None:
        raise ValueError("Base URL is missing. Please provide valid credentials.")
    clone_asset_premission(
        asset_id=target_asset_id,
        source_asset_id=source_asset_id,
        base_url=base_url,
    )


# To do: Add other permissions and make --no-auth-sub flag to be optional.
@app.command()
def set_permissions(
    asset_id: Annotated[
        str,
        typer.Option(
            "--asset-id",
            help="The asset ID of the form to delete.",
        ),
    ],
    no_auth_sub: Annotated[
        bool,
        typer.Option(
            help="Allow submission without authentication.",
        ),
    ],
) -> None:
    """
    Sets asset permissions.

    """
    _, base_url = get_credentials()
    if base_url is None:
        raise ValueError("Base URL is missing. Please provide valid credentials.")

    if no_auth_sub:
        submission_without_auth(asset_id=asset_id, base_url=base_url)


if __name__ == "__main__":
    app()
