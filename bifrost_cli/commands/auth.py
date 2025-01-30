from typing import Optional, Tuple

import keyring
import typer
from rich import print

app = typer.Typer()

SERVICE_NAME = "kobo-bifrost"


def save_credentials(api_key: str, api_url: str) -> None:
    """
    Save credentials to the keyring.

    Args:
        api_key (str): Kobo toolbox API key
        api_url (str): Kobo toolbox API URL
    """
    keyring.set_password(SERVICE_NAME, "api_key", api_key)
    keyring.set_password(SERVICE_NAME, "api_url", api_url)


def get_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Retrieve credentials from the keyring.

    Returns:
        tuple[str, str]: Api Key and API Url stored in keyrig
    """
    api_key = keyring.get_password(SERVICE_NAME, "api_key")
    api_url = keyring.get_password(SERVICE_NAME, "api_url")

    return api_key, api_url


def delete_credentials() -> None:
    """Delete credentials from the keyring."""
    api_key = keyring.get_password(SERVICE_NAME, "api_key")
    api_url = keyring.get_password(SERVICE_NAME, "api_url")

    if not api_key and not api_url:
        raise Exception("No credentials found")

    if api_key:
        keyring.delete_password(SERVICE_NAME, "api_key")
    if api_url:
        keyring.delete_password(SERVICE_NAME, "api_url")


@app.command()
def set_credentials(
    api_url: Optional[str] = typer.Option(None, prompt=False, help="Your API URL."),
    api_key: Optional[str] = typer.Option(None, prompt=False, help="Your API key."),
) -> None:
    """
    Set credentials by providing an API key and API URL.

    Args:
        api_url (str): Kobo toolbox API URL
        api_key (str): Kobo toolbox API key
    """
    existing_api_key, existing_api_url = get_credentials()

    if existing_api_key and existing_api_url:
        print(f"⚠️ You are already logged in with API URL: {existing_api_url}")
        overwrite = typer.confirm("Do you want to overwrite the existing credentials?")
        if not overwrite:
            print("✅ Existing credentials retained. No changes made.")
            return

    if not api_url:
        api_url = typer.prompt("Please enter your API URL")
    if not api_key:
        api_key = typer.prompt("Please enter your API key")

    if api_url is None or api_key is None:
        raise ValueError("API URL and API Key cannot be None.")

    save_credentials(api_key, api_url)
    print("✅ Credentials saved securely.")


@app.command()
def remove_credentials() -> None:
    """Clear saved API credentials (API key and API URL)."""
    try:
        delete_credentials()
        print("✅ Credentials removed.")
    except Exception:

        print("❌ No credentials were found to delete.")


@app.command()
def status() -> None:
    """Check the current credentials status."""
    api_key, api_url = get_credentials()
    if api_key and api_url:
        print(f"✅ You have set API credentials in with API URL: {api_url}")
    else:
        print("❌ You are not saved any API credentials.")


if __name__ == "__main__":
    app()
