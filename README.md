
# KOBO-Bifrost CLI

Commandline tool that helps you to create, update, deploy, redeploy, delete forms in Kobo-toolbox.



## Prerequisites 
1. Python v3.12.4. or greater should be installed. To install python. [install python](https://www.python.org/downloads/)
   
   To check python version installed on your system follow:
``` python
python --version
```
2. Create a Kobo-toolbox account [Signup kobotoolbox](https://eu.kobotoolbox.org/accounts/signup/)
3. Git should be already installed on your machine. To install git. [install git](https://git-scm.com/downloads)
   
## Installation and Update
To install/update Bifrost CLI Tool. Navigate to your terminal and run following command.
```python
pip install git+https://github.com/sankalpa-adhikari-sa/Kobo-bifrost-cli
```
*Note: It is recommended to install this package by creating a python virtual enviroment to avoid any conficts that may arise due to changes in dependencies packages version. This CLI tool uses click, requests and rich packages as dependencies*
After successfully installing the CLI tool. Navigate to your terminal (if you are using python enviroment first activate your python enviroment on which cli is installed) and use `bifrost` command to use it's funtions.

## Uninstall
To uninstall Bifrost CLI Tool. Naviagate to your terminal and run following command.
```python
pip uninstall bifrost-cli
```

## Commands

|Command|	Description	|Usage|
|-------|--------------|-------------|
|`list-assets`|	List all assets|	`bifrost list-assets`|
|`create <filepath>`	|Create a new form from the file at `<filepath>`	|`bifrost create <filepath> [-d, --deploy]`|
|`deploy <uid>`	|Deploy the form with the specified `<uid>`	|`bifrost deploy <uid>`|
|`update <uid> <filepath>`	|Update the form with the specified `<uid>` using the file at `<filepath>`	|`bifrost update <uid> <filepath> [-d, --deploy] [-rd, --redeploy]`|
|`redeploy <uid>`	|Redeploy the form with the specified `<uid>`	|`bifrost redeploy <uid>`|
|`remove <uid>`	|Remove the form with the specified `<uid>`	|`bifrost remove <uid>`|
|`set-permissions <uid`>	|Set permissions for the form with the specified `<uid>`	|`bifrost set-permissions <uid> [--no-auth-sub]`|
|`clone-permissions <source_uid> <target_uid>`|	Clone permissions from the form with `<source_uid>` to the form with `<target_uid>`	|`bifrost clone-permissions <source_uid> <target_uid>`|

## Configuration Commands

The config group allows you to set up and view your Bifrost CLI configuration.

|Command|	Description|	Usage|
|---|---|---|
|`config api-url <url>`|	Set the KoboToolbox API URL to `<url>`|	`bifrost config api-url <url>`|
|`config api-key <key>`	|Set the KoboToolbox API key to `<key>`|	`bifrost config api-key <key>`|
|`config view`	|Display the current configuration|	`bifrost config view`|
|`config downloads-path`|Set the Path to the folder for saving data and forms|`bifrost downloads-path <path_to_folder>`|
## Export Commands
The export command allows you to export your data in CSV or XLSX format
|Command|	Description|	
|---|---|
|`export csv <uid> <filename> [OPTIONS]`| Export data to CSV format | 
|`export xls <uid> <filename> [OPTIONS]`| Export data to XLS format | 

|Command|Short Options| Long Option|Values|Description|
|---|---|---|---|---|
|`csv` or `xls`| `-sep`|`--separator`|`TEXT`|Group Separator for data.|
|`csv` or `xls`| `-c`|`--current-version`||Include data from all Versions default=False|
|`csv` or `xls`| `-gh`| `--gheaders`  ||Include group headers in the export. default=True|
|`csv` or `xls`| `-lang`| `--language`|`[_default,_xml, <languagecode>]`|Language for the export: _default, _xml or language code. default=_default|
|`csv` or `xls`| `-nmu`|`--no-media-url`||Include media URL in the export. default=False|
|`csv` or `xls` | `-ms`|`--multiple-select`|`[details, both, summary]`|Export select many question as default=summary|
|`xls`| `-xt`|`--xtext`||Store data and number response as text. default=False|


## Example

To use Bifrost CLI you first need to setup your API URL and API Key.

#### Config Kobotoolbox API key ```config api-key``` 
```bash
bifrost config api-key CONFIG_API_KEY
```
#### Config Kobotoolbox API URL ```config api-url``` 
```bash
bifrost config api-url CONFIG_API_URL
```
#### View Config ```config view``` 
```bash
bifrost config view
```
#### Config Downloads folder path ```config downloads-path``` 
```bash
bifrost config downloads-path CONFIG_DOWNLOADS_PATH
```
#### Create Koboform ```create``` 
Creates a koboform as draft file.
```bash
bifrost create PATH_TO_XLS_FORM
```
#### Deploy Koboform ```deploy```

```bash
bifrost deploy ASSET_ID
```

#### Update Koboform ```update```

```bash
bifrost update ASSET_ID PATH_TO_XLS_FORM
```

#### Redeploy Updated Koboform ```redeploy```

```bash
bifrost redeploy ASSET_ID PATH_TO_XLS_FORM
```
#### Create and Deploy Koboform ```-d```

```bash
bifrost create PATH_TO_XLS_FORM -d
```
#### Update and Re-deploy Koboform ```-rd```

```bash
bifrost update ASSET_ID PATH_TO_XLS_FORM -rd
```

#### Remove a Koboform ```remove```
```bash
bifrost remove ASSET_ID
```
#### Download Data```csv|xls```
```bash
bifrost export xls ASSET_ID FILE_NAME -sep "/" -c -gh -lang "Nepali (ne)" -nmu -xt -ms "both"
```
*Note: Provide file name with correct extension you want the data to export. For example my_data.xlsx*
#### Enable submit data without username and password premission ```--no-auth-sub```
```bash
bifrost set-permissions ASSET_ID --no-auth-sub
```
#### Clone premission form another Koboform ```clone-permissions```
```bash
bifrost clone-permissions  SOURCE_ASSET_ID TARGET_ASSET_ID
```
```SOURCE_ASSET_ID```
 is the uid of Koboform form which you want to copy premission to your target form.
