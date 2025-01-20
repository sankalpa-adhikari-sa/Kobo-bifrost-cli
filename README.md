# KOBO-Bifrost CLI

Commandline tool that helps you to create, update, deploy, redeploy, delete forms in Kobo-toolbox.

## Prerequisites

1. Python v3.12.4. or greater should be installed. To install python. [install python](https://www.python.org/downloads/)

   To check python version installed on your system follow:

```python
python --version
```

2. Create a Kobo-toolbox account [Signup kobotoolbox](https://eu.kobotoolbox.org/accounts/signup/)

## Installation and Update

To install/update Bifrost CLI Tool. Navigate to your terminal and run following command.

```python
pip install git+https://github.com/sankalpa-adhikari-sa/Kobo-bifrost-cli.git@v0.0.1
```

\_Note: It is recommended to install this package by creating a python virtual enviroment to avoid any conficts that may arise due to changes in dependencies packages version.
After successfully installing the CLI tool. Navigate to your terminal (if you are using python enviroment first activate your python enviroment on which cli is installed) and use `bifrost` command to use it's funtions.

## Uninstall

To uninstall Bifrost CLI Tool. Naviagate to your terminal and run following command.

```python
pip uninstall bifrost
```

## Commands

| Command             | Description                                                                                             | Options                                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `init`              | Initializes a new project by creating a structured Excel workbook with optional conditional formatting. |                                                                                                            |
| `list-assets`       | Lists all assets with basic information                                                                 |                                                                                                            |
| `create`            | Creates a new asset in kobotoolbox                                                                      | `--filepath`<br> `[--deploy, -d]`                                                                          |
| `view`              | View asset snapshots                                                                                    | `--asset-id`                                                                                               |
| `deploy`            | Deploys an specified asset                                                                              | `--asset-id`                                                                                               |
| `update`            | Updates a specified existing asset                                                                      | `--asset-id`<br>`--filepath` <br>`[--deploy, -d]`<br> `[--redeploy, -rd]` <br>`[--preview-snapshots, -ps]` |
| `redeploy`          | Redeploys a specified asset                                                                             | `--asset-id`                                                                                               |
| `delete`            | Deletes a specified asset                                                                               | `--asset-id`                                                                                               |
| `asset xls`         | Downloads specified asset in Xls format.                                                                | `--asset-id`<br> `--download-path`                                                                         |
| `asset xml`         | Downloads specified asset in Xml format.                                                                | `--asset-id`<br> `--download-path`                                                                         |
| `set-permissions`   | Sets asset permissions                                                                                  | `--asset-id`<br> `--no-auth-sub`                                                                           |
| `clone-permissions` | Clones permissions from source project to another target project.                                       | `--from`<br> `--to`                                                                                        |

## Configuration Commands

The config group allows you to set up and view your Bifrost CLI configuration.

| Command              | Description                                          | Options                    |
| -------------------- | ---------------------------------------------------- | -------------------------- |
| `set-credentials`    | Set credentials by providing an API key and API URL. | `--api-key`<br>`--api-url` |
| `remove-credentials` | Clear saved API credentials (API key and API URL).   |                            |
| `status`             | Check the current credentials status.                | `bifrost config view`      |

## Export Commands

| Command                      | Option                     | Values                            | Description                                                                   |
| ---------------------------- | -------------------------- | --------------------------------- | ----------------------------------------------------------------------------- |
| `export csv` or `export xls` | `--output-name`            | `TEXT`                            | Output file name                                                              |
|                              | `--asset-id`               | `TEXT`                            | The asset ID of the asset to export data.                                     |
|                              | `--download-path`          | `TEXT`                            | Download path. Defaults to the current directory.                             |
|                              | `[--separator, -sep]`      | `TEXT`                            | Group Separator for data. Default= /                                          |
|                              | `[--current-version, -c]`  |                                   | Include data from all Versions default=False                                  |
|                              | `[--gheaders, -gh]`        |                                   | Include group headers in the export. default=True                             |
|                              | `[--language, -lang]`      | `[_default,_xml, <languagecode>]` | Language for the export: \_default, \_xml or language code. default=\_default |
|                              | `-[-no-media-url, -nmu]`   |                                   | Include media URL in the export. default=False                                |
|                              | `[--multiple-select, -ms]` | `[details, both, summary]`        | Export select many question as default=summary                                |
| `export xls`                 | `[--xtext, -xt]`           |                                   | Store data and number response as text. default=False                         |

## Example

To use Bifrost CLI you first need to setup your API URL and API Key.

#### Configure Kobotoolbox Credentials `set-credentials`

```bash
bifrost set-credentials --api-key CONFIG_API_KEY --api-url CONFIG_API_URL
```

#### View Status `status`

```bash
bifrost status
```

#### Remove Kobotoolbox Credentials `remove-credentials`

```bash
bifrost remove-credentials
```

#### Initialize a new project `init`

Creates a new XLS form locally.

```bash
bifrost init
```

#### Create Koboform in Kobotoolbox platform `create`

Creates a koboform as draft file in kobotoolbox.

```bash
bifrost create --filepath PATH_TO_XLS_FORM
```

#### Deploy Koboform `deploy`

```bash
bifrost deploy --asset-id ASSET_ID
```

#### View Koboform snapshot `view`

```bash
bifrost view --asset-id ASSET_ID
```

#### Update Koboform `update`

```bash
bifrost update --asset-id ASSET_ID --filepath PATH_TO_XLS_FORM
```

#### Redeploy Updated Koboform `redeploy`

```bash
bifrost redeploy --asset-id ASSET_ID
```

#### Create and Deploy Koboform `-d`

```bash
bifrost create --filepath PATH_TO_XLS_FORM -d
```

#### Update and Re-deploy Koboform `-rd`

```bash
bifrost update --asset-id ASSET_ID --filepath PATH_TO_XLS_FORM -rd
```

#### Delete a Koboform `delete`

```bash
bifrost delete --asset-id ASSET_ID
```

#### Download Data`csv|xls`

```bash
bifrost export xls --asset-id ASSET_ID --output-name FILE_NAME --download-path DOWNLOAD_DIR_PATH -sep "/" -c -gh -lang "Nepali (ne)" -nmu -xt -ms "both"
```

#### Enable submit data without username and password premission `--no-auth-sub`

```bash
bifrost set-permissions --asset-id ASSET_ID --no-auth-sub
```

#### Clone premission form another Koboform `clone-permissions`

```bash
bifrost clone-permissions  --from SOURCE_ASSET_ID --to TARGET_ASSET_ID
```

`SOURCE_ASSET_ID`
is the uid of Koboform form which you want to copy premission to your target form.

## Autofill asset-id, download-path, file-path.

Additionally Bifrost cli creates `.bifrost/info.txt` folder in your project directory which saves asset-id , download-path, and file-path while using the commands. If the arguments are not provided bifrost uses the values from the `bifrost/info.txt` file.

For example:

If both ASSET_ID and PATH_TO_XLS_FORM is availabe in info.txt file

```bash
bifrost update --asset-id ASSET_ID --filepath PATH_TO_XLS_FORM
```

will be reduced to just

```bash
bifrost update
```
