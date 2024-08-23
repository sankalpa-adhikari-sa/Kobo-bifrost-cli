
# KOBO-Bifrost CLI

Commandline tool that helps you to create, update, deploy, redeploy, delete forms in Kobo-toolbox.



## Prerequisites 
1. Python v3.12.4. or greater should be installed. To check python version instlled on your system follow:

``` python
python --version
```
2. Create a Kobo-toolbox account [Signup kobotoolbox](https://eu.kobotoolbox.org/accounts/signup/)
## Environment Variables

To run this project, you will need to add the following environment variables to your .env file alongside of `bifrost.py` file

```
KOBO_API_BASE_URL = YOUR_API_URL
```

```
KOBO_API_KEY = YOUR_API_KEY
````
## Options

| Short Option | Long Option | Arguments | Description |
|--------------|-------------|-----------|-------------|
| `-h` | `--help` | | Shows help message and exit |
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

#### 1. Create Koboform ```-c``` 
Creates a koboform as draft file.
```bash
python bifrost.py -c PATH_TO_XLS_FORM
```
#### 2. Deploy Koboform ```-d```

```bash
python bifrost.py -d ASSET_ID
```
*Note: You cannot deploy form that is already deployed but can Redeploy the existing form. To redeploy use ```-rd``` flag*

#### 3. Update Koboform ```-u```

```bash
python bifrost.py -u ASSET_ID PATH_TO_XLS_FORM
```
#### 4. Redeploy Updated Koboform ```-rd```

```bash
python bifrost.py -u ASSET_ID PATH_TO_XLS_FORM
```

#### 5. Create and Deploy Koboform ```-cd```

```bash
python bifrost.py -cd PATH_TO_XLS_FORM
```
#### 6. Update and Re-deploy Koboform ```-urd```

```bash
python bifrost.py -urd ASSET_ID PATH_TO_XLS_FORM
```
#### 7. Remove a Koboform ```-rm```
```bash
python bifrost.py -rm ASSET_ID
```
#### 8. Enable submit dat without username and password premission ```-swa```
```bash
python bifrost.py -swa ASSET_ID
```
#### 9. Clone premission form another Koboform ```-pc```
```bash
python bifrost.py -pc TARGET_ASSET_ID SOURCE_ASSET_ID
```
```SOURCE_ASSET_ID```
 is the uid of Koboform form which you want to copy premission to your target form.

