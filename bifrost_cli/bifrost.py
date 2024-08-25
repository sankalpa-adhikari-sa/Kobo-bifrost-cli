import click
import json
import os
import requests
from rich.console import Console
from rich.table import Table
from typing import Optional, Union
import time
import functools

CONFIG_FILE = os.path.expanduser('~/.bifrost_config.json')

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def ensure_config(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        config = load_config()
        if not config.get('KOBO_API_BASE_URL') or not config.get('KOBO_API_KEY')  or not config.get('KOBO_DOWNLOADS'):
            click.echo("API URL or API Key not set. Let's configure them now.")
            if not config.get('KOBO_API_BASE_URL'):
                config['KOBO_API_BASE_URL'] = click.prompt("Please enter the API URL")
            if not config.get('KOBO_API_KEY'):
                config['KOBO_API_KEY'] = click.prompt("Please enter the API Key", hide_input=True)
            if not config.get('KOBO_DOWNLOADS'):
                config['KOBO_DOWNLOADS'] = click.prompt("Please enter the path to folder to save data/assets", hide_input=True)
            save_config(config)
            click.echo("Configuration saved.")
        return f(*args, **kwargs)
    return wrapper

class Bifrost:
    def __init__(self,base_url:str,api_key:str) -> None:
        self.base_url = base_url if base_url.endswith("/") else f"${base_url}/"
        self.api_key= api_key
        self.headers = {'Authorization': f'Token {self.api_key}'}
        

    def _make_request(self, method:str, url:str, **kwargs) -> requests.Response:
        try:
           response= requests.request(method=method, url=url, headers=self.headers,**kwargs)
           response.raise_for_status()
           return response
        except requests.RequestException as e:
            print(f"Error during making {method} request: {e}")

    def _check_status(self,url:str) -> dict:
        return self._make_request("GET", url=url).json()
    
    def _wait_for_completion(self, url:str)-> Union[None,dict]:
        while True :
            status_response = self._check_status(url)
            if status_response['status'] == 'processing':
                print("Status: still processing. Checking again in a few seconds...")
                time.sleep(10)
            elif status_response["status"]=="complete":
                    print("Status: completed successfully.")
                    return status_response
            else:
                print("Something went wrong!")
                break
    def _import_form (self, url:str, data:dict, file_path:Optional[str]= None) -> None:
        if file_path is None:
            raise ValueError("File path is not provided.")
        try:
            with open(file_path, 'rb') as file:
                imported_xls_form = {'file': file}
               
                response = self._make_request("POST", url, data=data, files=imported_xls_form, params={'format': 'json'})

                if response.status_code== 201:
                    response_data= response.json()
                    current_form_import_url= response_data["url"]
                    print(f"Import started. Checking status at: {current_form_import_url}")
                    import_response= self._wait_for_completion(current_form_import_url)
                    return import_response
                else:
                    print(f"Failed to start import. Status code: {response.status_code}")
                    print(response.text)

        except FileNotFoundError:
            print(f"File not found: {file_path}")

    def get_all_asset(self)-> None:
        asset_url= f"{self.base_url}assets/"
        def determine_modification_status(deployed_version_id, version_id):
            if deployed_version_id is None:
                return "-"
            return "No" if version_id == deployed_version_id else "Yes"
        
        response= self._make_request("GET", asset_url, params={'format': 'json'})
        table = Table(title="List of Assets")
        table.add_column("SN", justify="right", no_wrap=True)
        table.add_column("Name",overflow="fold")
        table.add_column("AssetID", justify="right",overflow="fold")
        table.add_column("Deployment status", justify="right")
        table.add_column("Undeployed Update", justify="right")
        table.add_column("Submission Count", justify="right")
        for index,asset in enumerate(response.json()["results"]):
            modification_status = determine_modification_status(
            asset.get("deployed_version_id"),
            asset.get("version_id"))
            table.add_row(f"{index+1}", asset["name"], asset["uid"], asset["deployment_status"], modification_status, f"{asset["deployment__submission_count"]}")
        console = Console()
        console.print(table)


    def create_form(self, file_path:Optional[str]= None)->None:
        import_url= self.base_url +"imports/"
        data = {'library': 'false'}
        print("Starting Form Creation Procedure.......")
        response= self._import_form(url=import_url, data=data,file_path=file_path)
        res= response["messages"]["created"][0]
        table = Table(title="Information of created asset")
        table.add_column("SN", justify="right", no_wrap=True)
        table.add_column("AssetID", justify="right",overflow="fold")
        table.add_column("Owner", justify="right",overflow="fold")
        table.add_column("creation", justify="right",overflow="fold")
        table.add_row(f"1", res["uid"], res["owner__username"],"successful")
        console = Console()
        console.print(table)
        return res["uid"]
        

    def update_form(self, form_id:str,  file_path:Optional[str]= None)-> None:
        import_url = f"{self.base_url}imports/"
        form_asset_url = f"{self.base_url}assets/{form_id}/"
        data = {'library': 'false', 'destination': form_asset_url, 'assetUid': form_id}
        print("Starting Form Update procedure.......")
        self._import_form(url=import_url, data=data, file_path=file_path)
        

    def deploy_form(self, form_id:str):
        deployment_url = f"{self.base_url}assets/{form_id}/deployment/"
        deployment_data= {
            "active": True
        }
        print("Starting Form Deployment procedure.......")
        response = self._make_request("POST", deployment_url, data=deployment_data,params={'format': 'json'})

        if type(response) == type(None):
            print("Error: The form cannot be deployed because it may have been deployed already. Please check the deployment status of the form and ensure it is not deployed previously before attempting to deploy.")
            return
        res= response.json()
        table = Table(title="Deployment Details")
        table.add_column("SN", justify="right", overflow="fold")
        table.add_column("Asset ID", justify="right",overflow="fold")
        table.add_column("Deployment Status", justify="right",overflow="fold")
        table.add_column("Deployment Link", justify="right",overflow="fold")
       
        table.add_row(f"1", form_id, res["asset"]["deployment_status"], res["asset"]["deployment__links"]["url"])
        console = Console()
        console.print(table)
    
    def redeploy_form (self, form_id:str):
        form_asset_url = f"{self.base_url}assets/{form_id}/"
        deployment_url = f"{self.base_url}assets/{form_id}/deployment/"
        print("Starting Form Re-deployment procedure......")
        response = self._make_request("GET", form_asset_url, params={'format': 'json'})
        version_to_deploy = response.json()['version_id']
        
        deployment_data = {
            'version_id': version_to_deploy,
            "active": True
        }
        
        response = self._make_request("PATCH", deployment_url, data=deployment_data, params={'format': 'json'})
        if type(response) == type(None):
            print("Error: The form cannot be redeployed because it may not have been deployed yet. Please check the deployment status of the form and ensure it is deployed before attempting to redeploy.")
            return
        if response.status_code == 200:
            print("Successfully Re-deployed form")
            
        res= response.json()
        table = Table(title="Re-deployment Details")
        table.add_column("SN", justify="right",overflow="fold")
        table.add_column("Asset ID", justify="right",overflow="fold")
        table.add_column("Deployment Status", justify="right",overflow="fold")
        table.add_column("v.SN", justify="right",overflow="fold")
        table.add_column("v.ID", justify="right",overflow="fold")
        table.add_column("Deployment Link", justify="right",overflow="fold")
        table.add_column("Submission Count", justify="right",overflow="fold")
        table.add_row(f"1", form_id, res["asset"]["deployment_status"],f"{res["asset"]["version_count"]}", res["asset"]["deployed_version_id"],  res["asset"]["deployment__links"]["url"], f"{res["asset"]["deployment__submission_count"]}")
        console = Console()
        console.print(table)

    def delete_form(self, form_id:str)-> None:
        form_asset_url = f"{self.base_url}assets/{form_id}/"
        print("Starting Form Deletion Procedure.......")
        self._make_request("DELETE", form_asset_url)
        print("Succssfully Deleted Form")

    def submission_without_auth (self,form_id:str)->None:
        premission_url= f"{self.base_url}assets/{form_id}/permission-assignments/"
        premission={"user":"https://eu.kobotoolbox.org/api/v2/users/AnonymousUser/",
                    "permission":"https://eu.kobotoolbox.org/api/v2/permissions/add_submissions/"}
        response= self._make_request("POST", url=premission_url, data=premission)
        if response.status_code == 201:
            print("Successfuly updated premission to submit data without auth")
    
    def clone_premission(self, form_id:str, source_id:str) -> None:
        clone_premission_url= f"{self.base_url}assets/{form_id}/permission-assignments/clone/"
        cloned_premissions={"clone_from": source_id}
        response= self._make_request("PATCH", url=clone_premission_url, data=cloned_premissions)
        if response.status_code == 200:
            print(f"Successfuly cloned premission from \n source_asset_id: {source_id}")
    
    def export_data(self, form_id:str, file_path:str, export_options)-> None:
        exports_url= f"{self.base_url}assets/{form_id}/exports/"
        response= self._make_request(method="POST", url=exports_url, data= export_options,params={'format': 'json'} )
        if type(response) == type(None):
            print("Somthing went Wrong! Try again....")
            return
        exp= response.json()["url"]
        data_url_res= self._wait_for_completion(url=exp)
        if type(data_url_res) == type(None):
            print("Somthing went Wrong! Try again....")
            return
        data_res= self._make_request(method="GET", url=data_url_res["result"] )
        if data_res.status_code == 200:
             with open(file_path, "wb") as file:
                file.write(data_res.content)
                print(f"File downloaded successfully and saved to {file_path}.")
        else:
                print(f"Failed to download file. Status code: {data_res.status_code}")
        
    pass

@click.group()
def cli():
    """Bifrost CLI for interacting with KoboToolbox API"""
    pass

@cli.command()
@ensure_config
def list_assets():
    """List all assets"""
    config = load_config()
    bifrost = Bifrost(config['KOBO_API_BASE_URL'], config['KOBO_API_KEY'])
    bifrost.get_all_asset()

@cli.command()
@click.argument('filepath')
@click.option('-d', '--deploy', is_flag=True, help='Deploy the form after creation')
@ensure_config
def create(filepath, deploy):
    """Create a new form"""
    config = load_config()
    bifrost = Bifrost(config['KOBO_API_BASE_URL'], config['KOBO_API_KEY'])
    form_id = bifrost.create_form(filepath)
    if deploy and form_id:
        bifrost.deploy_form(form_id)

@cli.command()
@click.argument('uid')
@ensure_config
def deploy(uid):
    """Deploy a form"""
    config = load_config()
    bifrost = Bifrost(config['KOBO_API_BASE_URL'], config['KOBO_API_KEY'])
    bifrost.deploy_form(uid)

@cli.command()
@click.argument('uid')
@click.argument('filepath')
@click.option('-rd', '--redeploy', is_flag=True, help='Redeploy the deployed form after update')
@click.option('-d', '--deploy', is_flag=True, help='Deploy the draft form after update')
@ensure_config
def update(uid, filepath, deploy, redeploy):
    """Update a form"""
    config = load_config()
    bifrost = Bifrost(config['KOBO_API_BASE_URL'], config['KOBO_API_KEY'])
    bifrost.update_form(uid, filepath)
    if deploy:
        bifrost.deploy_form(uid)
    if redeploy:
        bifrost.redeploy_form(uid)

@cli.command()
@click.argument('uid')
@ensure_config
def redeploy(uid):
    """Redeploy a form"""
    config = load_config()
    bifrost = Bifrost(config['KOBO_API_BASE_URL'], config['KOBO_API_KEY'])
    bifrost.redeploy_form(uid)

@cli.command()
@click.argument('uid')
@ensure_config
def remove(uid):
    """Remove a form"""
    config = load_config()
    if click.confirm("This will permanently delete your form and its data. Are you sure you want to continue?"):
        bifrost = Bifrost(config['KOBO_API_BASE_URL'], config['KOBO_API_KEY'])
        bifrost.delete_form(uid)

@cli.command()
@click.argument('uid')
@click.option('--no-auth-sub', is_flag=True, help='allow data submission without authentication.')
@ensure_config
def set_permissions(uid, no_auth):
    """Set form permissions"""
    config = load_config()
    bifrost = Bifrost(config['KOBO_API_BASE_URL'], config['KOBO_API_KEY'])
    if no_auth:
        bifrost.submission_without_auth(uid)

@cli.command()
@click.argument('source_uid')
@click.argument('target_uid')
@ensure_config
def clone_permissions(source_uid, target_uid):
    """Clone permissions from [Source] one form to another [Target]"""
    config = load_config()
    bifrost = Bifrost(config['KOBO_API_BASE_URL'], config['KOBO_API_KEY'])
    bifrost.clone_premission(target_uid, source_uid)

@cli.group()
def export():
    """Export data in various formats."""
    pass

@export.command('csv')
@click.argument('uid')
@click.argument('file_name')
@click.option('-sep', '--separator', default='/', help='Group Separator for data.')
@click.option('-c', '--current-version',is_flag=True, default=True, help='Include data from all Versions')
@click.option('-gh', '--gheaders', is_flag=True, default=False, help='Include group headers in the export.')
@click.option('-lang', '--language', default='_default', help='Language for the export: _default, _xml or language code.')
@click.option('-nmu', '--no-media-url', is_flag=True, default=True, help='Include media URL in the export.')
@click.option('-ms', '--multiple-select',  type=click.Choice(["details","both","summary"]), default='summary', help='Include media URL in the export.')
@ensure_config
def export_csv(uid, current_version, file_name, separator,multiple_select, gheaders, language, no_media_url):
    """Export data as CSV."""
    config = load_config()
    bifrost = Bifrost(config['KOBO_API_BASE_URL'], config['KOBO_API_KEY'])
    datapath = os.path.join(config["KOBO_DOWNLOADS"], file_name)

    export_options = {
        "fields":[],
        'type': 'csv',
        "fields_from_all_versions":current_version,
        'group_sep': separator,
        'hierarchy_in_labels': gheaders,
        'lang': language,
        "multiple_select":multiple_select,
        'include_media_url': no_media_url,
        'xls_types_as_text':False
    }
    
    bifrost.export_data(form_id=uid, file_path=datapath, export_options=export_options)

@export.command('xls')
@click.argument('uid')
@click.argument('file_name')
@click.option('-sep', '--separator', default='/', help='Group Separator for data.')
@click.option('-c', '--current-version',is_flag=True, default=True, help='Include data from all Versions')
@click.option('-gh', '--gheaders', is_flag=True, default=False, help='Include group headers in the export.')
@click.option('-lang', '--language', default='_default', help='Language for the export: _default, _xml or language code.')
@click.option('-nmu', '--no-media-url', is_flag=True, default=True, help='Include media URL in the export.')
@click.option('-xt', '--xtext', is_flag=True, default=False, help='Store data and number response as text.')
@click.option('-ms', '--multiple-select',  type=click.Choice(["details","both","summary"]), default='summary', help='Include media URL in the export.')
@ensure_config
def export_xls(uid,xtext, current_version, file_name, separator,multiple_select, gheaders, language, no_media_url):
    """Export data as XLS."""
    config = load_config()
    bifrost = Bifrost(config['KOBO_API_BASE_URL'], config['KOBO_API_KEY'])
    datapath = os.path.join(config["KOBO_DOWNLOADS"], file_name)

    export_options = {
        "fields":[],
        'type': 'xls',
        "fields_from_all_versions":current_version,
        'group_sep': separator,
        'hierarchy_in_labels': gheaders,
        'lang': language,
        "multiple_select":multiple_select,
        'include_media_url': no_media_url,
        'xls_types_as_text':xtext
    }
    
    bifrost.export_data(form_id=uid, file_path=datapath, export_options=export_options)

@cli.group()
def config():
    """Configure Bifrost CLI"""
    pass

@config.command()
@click.argument('url')
def api_url(url):
    """Set the API URL"""
    config = load_config()
    config['KOBO_API_BASE_URL'] = url
    save_config(config)
    click.echo("API URL has been set.")

@config.command()
@click.argument('key')
def api_key(key):
    """Set the API key"""
    config = load_config()
    config['KOBO_API_KEY'] = key
    save_config(config)
    click.echo("API key has been set.")

@config.command()
@click.argument('folder_path')
def downloads_path(folder_path):
    """Set the Path to the folder for saving data and forms"""
    config = load_config()
    config['KOBO_DOWNLOADS'] = folder_path
    save_config(config)
    click.echo("Downloads path has been set.")

@config.command()
def view():
    """View current configuration"""
    if click.confirm("This will display sensitive data. Are you sure you want to continue?"):
        config = load_config()
        click.echo(f"API URL: {config.get('KOBO_API_BASE_URL', 'Not set')}")
        click.echo(f"API Key: {config.get('KOBO_API_KEY', 'Not set')}")
        click.echo(f"Downloads Path: {config.get('KOBO_DOWNLOADS', 'Not set')}")

   
def main():
    cli()
if __name__ == "__main__":
    main()