import argparse
import json
import os
import requests
from rich.console import Console
from rich.table import Table
from typing import Optional, Union
import time
CONFIG_FILE = os.path.expanduser('~/.bifrost_config.json')

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def set_config(key, value):
    config = load_config()
    config[key] = value
    save_config(config)
    print(f"{key.capitalize()} has been set.")

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
    
    def _wait_for_import_completion(self, current_form_import_url:str)-> Union[None,dict]:
        while True :
            status_response = self._check_status(current_form_import_url)
            if status_response['status'] == 'processing':
                print("Import is still processing. Checking again in a few seconds...")
                time.sleep(10)
            elif status_response["status"]=="complete":
                    print("XLS form import has completed successfully.")
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
                    import_response= self._wait_for_import_completion(current_form_import_url)
                    return import_response
                else:
                    print(f"Failed to start import. Status code: {response.status_code}")
                    print(response.text)

        except FileNotFoundError:
            print(f"File not found: {file_path}")

    def get_all_asset(self)-> None:
        asset_url= f"{self.base_url}assets/"
        response= self._make_request("GET", asset_url, params={'format': 'json'})
        table = Table(title="List of Assets")
        table.add_column("SN", justify="right", no_wrap=True)
        table.add_column("Name",overflow="fold")
        table.add_column("AssetID", justify="right",overflow="fold")
        table.add_column("Deployment status", justify="right")
        table.add_column("Submission Count", justify="right")
        for index,asset in enumerate(response.json()["results"]):
            table.add_row(f"{index+1}", asset["name"], asset["uid"], asset["deployment_status"], f"{asset["deployment__submission_count"]}")
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
        
    pass

def main():
    config = load_config()
    
    parser = argparse.ArgumentParser(description="KOBO-Bifrost - CLI for CRUD application")
    parser.add_argument("--config-api-key", help="Set the API key")
    parser.add_argument("--config-api-url", help="Set the API URL")
    parser.add_argument("-ga", "--get-all", action="store_true", help="Gets all Kobo form UIDs and names")
    parser.add_argument("-c", "--create", metavar="FILEPATH", help="Creates a new form as draft")
    parser.add_argument("-rm", "--delete", metavar="ASSET_ID", help="Deletes the specified form")
    parser.add_argument("-cd", "--create-deploy", metavar="FILEPATH", help="Creates and deploys a new form")
    parser.add_argument("-u", "--update", nargs=2, metavar=("ASSET_ID", "FILEPATH"), help="Updates a Kobo form")
    parser.add_argument("-d", "--deploy", metavar="ASSET_ID", help="Deploys a form")
    parser.add_argument("-rd", "--redeploy", metavar="ASSET_ID", help="Redeploys a form")
    parser.add_argument("-urd", "--update-redeploy", nargs=2, metavar=("ASSET_ID", "FILEPATH"), help="Updates and redeploys a form")
    parser.add_argument("-swa", "--submit-without-auth", metavar="ASSET_ID", help="Enables 'Submit data without auth' feature")
    parser.add_argument("-pc", "--permission-clone", nargs=2, metavar=("TARGET_ASSET_ID", "SOURCE_ASSET_ID"), help="Clones permissions from another Kobo form")
    
    args = parser.parse_args()

    if args.config_api_key:
        set_config('KOBO_API_KEY', args.config_api_key)
        return

    if args.config_api_url:
        set_config('KOBO_API_BASE_URL', args.config_api_url)
        return

   
    api_key = config.get('KOBO_API_KEY')
    api_url = config.get('KOBO_API_BASE_URL')

    if not api_key or not api_url:
        print("API key or URL not set. Use --config-api-key and --config-api-url to set them.")
        return
    bifrost = Bifrost(api_url, api_key)

    if args.get_all:
        bifrost.get_all_asset()
    elif args.create:
        bifrost.create_form(args.create)
    elif args.delete:
        bifrost.delete_form(args.delete)
    elif args.create_deploy:
        form_id = bifrost.create_form(args.create_deploy)
        if form_id:
            bifrost.deploy_form(form_id)
    elif args.update:
        bifrost.update_form(args.update[0], args.update[1])
    elif args.deploy:
        bifrost.deploy_form(args.deploy)
    elif args.redeploy:
        bifrost.redeploy_form(args.redeploy)
    elif args.update_redeploy:
        bifrost.update_form(args.update_redeploy[0], args.update_redeploy[1])
        bifrost.redeploy_form(args.update_redeploy[0])
    elif args.submit_without_auth:
        bifrost.submission_without_auth(args.submit_without_auth)
    elif args.permission_clone:
        bifrost.clone_premission(args.permission_clone[0], args.permission_clone[1])
    else:
        parser.print_help()
   

if __name__ == "__main__":
    main()