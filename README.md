
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
4. 
## Installation
To install Bifrost CLI Tool. Navigate to your terminal and run following command.
```python
pip install git+https://github.com/sankalpa-adhikari-sa/Kobo-bifrost-cli
```
*Note: It is recommended to install this package by creating a python virtual enviroment to avoid any conficts that may arise due to changes in dependencies packages version. This CLI tool uses requests and rich packages as dependencies*
After successfully installing the CLI tool. Navigate to your terminal (if you are using python enviroment first activate your python enviroment on which cli is installed) and use `bifrost` command to use it's funtions.


## Options

Bifrost cli provides following options to execute.

| Short Option | Long Option | Arguments | Description |
|--------------|-------------|-----------|-------------|
| `-h` | `--help` | | Shows help message and exit |
|  | `--config-api-key` |`CONFIG_API_KEY` | Sets the KOBO API key |
|  | `--config-api-url` |`CONFIG_API_URL` | Sets the KOBO API Base URL |
| `-ga` | `--get-all` | | Gets all Kobo form UIDs and names |
| `-c` | `--create` | `FILEPATH` | Creates a new form as draft |
| `-rm` | `--delete` | `ASSET_ID` | Deletes the specified form |
| `-cd` | `--create-deploy` | `FILEPATH` | Creates and deploys a new form |
| `-u` | `--update` | `ASSET_ID FILEPATH` | Updates a Kobo form |
| `-d` | `--deploy` | `ASSET_ID` | Deploys a form |
| `-rd` | `--redeploy` | `ASSET_ID` | Redeploys a form |
| `-urd` | `--update-redeploy` | `ASSET_ID FILEPATH` | Updates and redeploys a form |
| `-swa` | `--submit-without-auth` | `ASSET_ID` | Enables 'Submit data without auth' feature |
| `-pc` | `--permission-clone` | `TARGET_ASSET_ID SOURCE_ASSET_ID` | Clones permissions from another Kobo form |

## Example

To use Bifrost CLI you first need to setup your API URL and API Key.

#### 1. Config Kobotoolbox API key ```--config-api-key``` 
```bash
bifrost --config-api-key CONFIG_API_KEY
```
#### 2. Config Kobotoolbox API URL ```--config-api-url``` 
```bash
bifrost --config-api-url CONFIG_API_URL
```
#### 3. Create Koboform ```-c``` 
Creates a koboform as draft file.
```bash
bifrost -c PATH_TO_XLS_FORM
```
#### 4. Deploy Koboform ```-d```

```bash
bifrost -d ASSET_ID
```
*Note: You cannot deploy form that is already deployed but can Redeploy the existing form. To redeploy use ```-rd``` flag*

#### 5. Update Koboform ```-u```

```bash
bifrost -u ASSET_ID PATH_TO_XLS_FORM
```
*Note: If draft Kobo form is updated. You can deploy your form using `-d` flag as redeployment before deployment is not possible. Using `-rd` flag causes code ot break.*

#### 6. Redeploy Updated Koboform ```-rd```

```bash
bifrost -u ASSET_ID PATH_TO_XLS_FORM
```
#### 7. Create and Deploy Koboform ```-cd```

```bash
bifrost -cd PATH_TO_XLS_FORM
```
#### 8. Update and Re-deploy Koboform ```-urd```

```bash
bifrost -urd ASSET_ID PATH_TO_XLS_FORM
```
*Note: Update and Redeployment of draft form is not possible and causes error. To avoid this issue you need ot update and deploy using `-u` flag and `-d` flag sequencially*

#### 9. Remove a Koboform ```-rm```
```bash
bifrost -rm ASSET_ID
```
#### 10. Enable submit dat without username and password premission ```-swa```
```bash
bifrost -swa ASSET_ID
```
#### 11. Clone premission form another Koboform ```-pc```
```bash
bifrost -pc TARGET_ASSET_ID SOURCE_ASSET_ID
```
```SOURCE_ASSET_ID```
 is the uid of Koboform form which you want to copy premission to your target form.

