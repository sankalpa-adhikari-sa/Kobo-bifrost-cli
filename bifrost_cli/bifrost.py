import typer

from bifrost_cli.commands.asset import app as asset_app
from bifrost_cli.commands.auth import app as auth_app
from bifrost_cli.commands.create import app as create_app
from bifrost_cli.commands.delete import app as delete_app
from bifrost_cli.commands.deploy import app as deploy_app
from bifrost_cli.commands.deployment_links import app as deployment_links_app
from bifrost_cli.commands.export import app as export_app
from bifrost_cli.commands.initialize import app as init_app
from bifrost_cli.commands.list_asset import app as list_asset_app
from bifrost_cli.commands.permissions import app as permissions_app
from bifrost_cli.commands.preview import app as preview_app
from bifrost_cli.commands.redeploy import app as redeploy_app
from bifrost_cli.commands.update import app as update_app

app = typer.Typer()

app.add_typer(
    auth_app,
)
app.add_typer(
    init_app,
)

app.add_typer(list_asset_app)
app.add_typer(deploy_app)
app.add_typer(redeploy_app)
app.add_typer(create_app)
app.add_typer(update_app)
app.add_typer(delete_app)
app.add_typer(preview_app)
app.add_typer(permissions_app)
app.add_typer(
    export_app, name="export", help="Export Project data in CSV or XLSx file."
)
app.add_typer(
    asset_app,
    name="asset",
    help="Download specified asset in  XML or XLSx format.",
)
app.add_typer(deployment_links_app)

if __name__ == "__main__":
    app()
