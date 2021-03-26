# Pathways backend

This repository contains the server for providing access to data about services for refugees and immigrants to BC.

We can import and serve up read-only services data from the BC-211 dataset, using the [HSDS](http://openreferral.readthedocs.io/en/latest/hsds/reference/) data format and [HSDA API](http://docs.openreferral.org/en/latest/) format.

## Entities

These are the entities of the data model:

![Entities](ENTITIES.png)

## Getting started

Clone the repository

```
git clone git@github.com:pg-irc/pathways-backend.git
```

Set up and activate a python v3 environment

```
cd pathways-backend/
python3 -m venv .venv
source .venv/bin/activate
```

Install the required python libraries for local development, including the English SpaCy data set for natural language processing

```
python -m pip install --upgrade pip
pip install wheel
pip install -r requirements/local.txt
python -m spacy download en
```

## Psycopg2 on Mac

PostgreSQL and Postgis are prerequisites for installing psycopg2

```
brew install postgres
brew install postgis
```

If the pip install consistenly breaks for installing psycopg2, install the biniary version as follows

```
pip install psycopg2-binary
```

## PostgreSQL on non-Ubuntu systems

Create a PostgreSQL user and database for your local development and enable the PostGIS extension.
The user needs superuser permissions because the GIS extension needed for proximity search needs
to be installed on test databases as part of the unit tests and only superusers are allowed to do
that.

```
$ psql postgres
postgres=# CREATE USER pathways WITH PASSWORD 'your-secure-password';
postgres=# ALTER ROLE pathways SUPERUSER NOCREATEROLE CREATEDB;
postgres=# CREATE DATABASE pathways_local;
postgres=# GRANT ALL PRIVILEGES ON DATABASE pathways_local TO pathways;
postgres=# \connect pathways_local
postgres=# CREATE EXTENSION postgis;
```

Create a .env file and add your database user password

```
echo "POSTGRES_PASSWORD='your-secure-password'" > .env
```

To execute the test suite in production, where a database connection string is used, use a command line

```
DATABASE_URL=postgres://pathways:password@localhost/pathways_local \
MAILGUN_SENDER_DOMAIN=mailgun.org DJANGO_MAILGUN_API_KEY=xyz \
DJANGO_AWS_STORAGE_BUCKET_NAME=*bucket* \
DJANGO_SECRET_KEY=xyz ./manage.py test
```

## PostgreSQL on Ubuntu systems

PostgreSQL is locked down and very secure by default on Ubuntu, so there is a simpler and more
secure way to use on Ubuntu. Create a postgreql account with same name as your Linux account,
('rasmus' below) and make it superuser. You will be able to log into this postgresql account
without a password:

```
$ sudo -u postgres createuser --interactive
Enter name of role to add: rasmus
Shall the new role be a superuser? (y/n) y
```

Log into postgresql as the root account (postgresql) and set up the database and set some properties
on the user account:

```
$ sudo -u postgres psql
postgres=# ALTER ROLE rasmus SUPERUSER NOCREATEROLE CREATEDB;
postgres=# CREATE DATABASE pathways_local;
postgres=# GRANT ALL PRIVILEGES ON DATABASE pathways_local TO rasmus;
```

Now check that you can log in to psql as yourself with no password and that you have permission to
install the postgis extension:

```
$ psql -d pathways_local
postgres=# CREATE EXTENSION postgis;
```

Now the `.env` file needs to contain the postgresql username only:

```
echo "POSTGRES_USER=rasmus" > .env
```

## Create the database tables

```
python manage.py migrate
```

Create the django administration account:

```
python manage.py createsuperuser
```

Run the unit tests

```
python manage.py test
```

Start the API server

```
python manage.py runserver
```

You should now be able to access the server at http://127.0.0.1:8000/v1/. The Django admin tool is at http://127.0.0.1:8000/v1/admin/, and the question and choice entities are available at http://127.0.0.1:8000/v1/questions/ and http://127.0.0.1:8000/v1/questions/1/choices/.

## Import BC-211 data

We suppport two input formats for service provider data, iCarol XML and BC211 CSV. To import the XML data, this is the command to run

```
python manage.py import_icarol_xml ~/path/to/AIRSXML_2252_Export_20170109050136__211.xml

```

Importing from BC211 CSV is a two step process, where the first step converts the non-standard CSV into the [OpenReferral standard CSV](https://github.com/openreferral/sample-HSDS-datapackage) and the second step imports from those files into the database. Currently the preferred method is to use the CSV, because that is the format that is most convenient for BC211 to work with.

```
mkdir tmp_folder
./manage.py convert_icarol_csv ~/path/to/iCarolExport-BC211-Resources-20201112_mod.csv temp_folder/
./manage.py import_open_referral_csv temp_folder/
```

## Using different settings

By default the local settings are used. To use other settings, use the environment variable `DJANGO_SETTINGS_MODULE`, valid values are `config.settings.local`, `config.settings.test` and `config.settings.production`.

## Running tests on Travis and locally

Travis runs the tests using the settings in `config.settings.test`, against postgres using the accont "postgres" with empty password, creating a database called "test_db". To run the same tests locally, create a postgres user and a database called "test_db" owned by that user, and specify the postgres account using environment variables `POSTGRES_USER` and `POSTGRES_PASSWORD`, either on the command line:

```
DJANGO_SETTINGS_MODULE=config.settings.test POSTGRES_USER=test_user POSTGRES_PASSWORD='the_password' python manage.py test
```

or put these settings in a file called .env (use env.example as a template) and `export DJANGO_READ_DOT_ENV_FILE=True` to make sure the file is read.

## Upgrading packages

There is a utility script that may be used to update the python packages. Before using it, it may be a good idea to make sure that you have a correct environment based off of the requirements for the _local_ environment.

```
deactivate
rm -r .venv-local/
python3 -m venv .venv-local
source ./.venv-local/bin/activate
pip install -r requirements/local.txt
python -m spacy download en
```

Then run the upgrade script for either local, rest or production environment, e.g.:

```
./utility/upgrade_packages.sh production
```

You will be prompted to decide which of the possible upgrades you will take (this is using [pur](https://pypi.python.org/pypi/pur) in interactive mode), the requirement files are updated and a new environment is created using the new packages for use in testing before the upgrades are committed.

## Deploying to Heroku

### Prepare data

To deploy on Heroku from an empty production database: First prepare the deployment
files locally using the `utility/prepare_deploy.sh` script. It should be called with three
arguments

- Path to the XML file containing the BC211 data
- Path to the folder containing the Newcomers Guide content
- Path to the output file to generate, must end in `.json`

Upload the resulting json file to AWS so that it can be accessed from Heroku.

### Create the server

Ensure ALLOWED_HOSTS in the production settings include the name of the heroku instance.

These steps are for creating a new Heroku instance from scratch:

- Create an instance on Heroku, give it a name
- Under Resources, add a Heroku Postgres add-on, using the Hbby Basic level to support our amount of data
- Under Deploy, connect it to github using the pg-irc organization and the pathways-backend repo
- Under Settings, set all the environment variables (DATABASE_URL should already be there from the step above, you'll need that later)

| Variable                       | Value                             |
| ------------------------------ | --------------------------------- |
| DJANGO_SETTINGS_MODULE         | config.settings.production_heroku |
| DJANGO_READ_DOT_ENV_FILE       | False                             |
| BUILD_WITH_GEO_LIBRARIES       | 1                                 |
| MAILGUN_SENDER_DOMAIN          | mailgun.org                       |
| DJANGO_AWS_STORAGE_BUCKET_NAME | the bucket                        |
| DJANGO_SERVER_EMAIL            | the email                         |
| DJANGO_MAILGUN_API_KEY         | the key                           |
| DJANGO_SECRET_KEY              | the key                           |

- Under Deploy, Manual deploy, select git branch to deploy to the instance, then deploy it. This will take a while.

### Populate the server

- From bash, log into the server with
```
heroku ps:exec -a *appname*
```

- From bash, it is also simple to log into the database:
```
heroku pg:psql -a *appname*
```

- Set environment variables in shell, using the DATABASE_URL from the Settings, see abovve

```
export DJANGO_SETTINGS_MODULE=config.settings.production
export DJANGO_READ_DOT_ENV_FILE=False
export MAILGUN_SENDER_DOMAIN="example.com"

export DJANGO_AWS_STORAGE_BUCKET_NAME="the bucket"
export DJANGO_SECRET_KEY="the key"
export DJANGO_MAILGUN_API_KEY="the key"
export DATABASE_URL="value from Settings"
```

- Use wget to get the database dump file from AWS-S3
- Load the data

```
./manage.py loaddata *file.json*
```

- Then open the app, go to swagger and fire requests

## Getting started with docker

Create and launch the docker containers for local development

```
docker-compose -f compose-local.yml build
```

Set up the database inside the container

```
docker-compose -f compose-local.yml run django python manage.py migrate
docker-compose -f compose-local.yml run django python manage.py createsuperuser
```

Launch the container

```
docker-compose -f compose-local.yml up
```

and check out http://localhost:8000/ to see if it worked. See https://cookiecutter-django.readthedocs.io/en/latest/developing-locally-docker.html for more details.

## Getting started with PostgreSQL and PostGIS

PostgreSQL with the PostGIS extension is required for local development.
You can find the installation that is right for your OS here: https://www.postgresql.org/download/ or use a package manager
of your choice. The PostGIS extension can be found here: https://postgis.net/install/.

## Translations

Certain content is translatable, using [django-parler](http://django-parler.readthedocs.io/). The _translation_ module provides management commands to export translatable strings as POT files, and import their translations from PO files.

List available translatable models:

    ./manage.py content_translation_list_models

Create a POT file for a particular translatable model:

    ./manage.py content_translation_export organizations.organization > organization.pot

Or create a PO file with a model's current French translations:

    ./manage.py content_translation_export organizations.organization --language=fr > fr/organization.po

The resulting files can be edited in an application such as [GTranslator](https://wiki.gnome.org/Apps/Gtranslator) or [Poedit](https://poedit.net/).

After a translation file has been modified, you can import it again:

    ./manage.py content_translation_import fr/organization.po

## Importing Newcomers Guide content

Converting the Newcomers' Giude content into a form that can be built into the client is done using
a server side tool. This is an interrim measure only. Ultimately we will change this tool to instead
import the same data into the database, hence it makese sense to build it on the server side.

Prepare the Newcomers Guide content as documented elsewhere. Convert the content from its plain Unicode text
format to typescripts suitable for compiling into the client using the following server command:

    ./manage.py generate_client_fixtures path/to/newcomers/guide/content

This produces a number of typescript files in the working directory. Move these files into the client
folder structure

    mv *.ts ../pathways-frontend/src/fixtures/newcomers_guide/

Build the client as normal, noting that the screen output contains the line `bin/buildFixtures.sh: Using Newcomers Guide fixtures` to indicate that the Newcomers' Guide content is being used.

## Development

### Null and django blank

Required string fields should never be null and never be the empty string. Optional string fields should never be the empty string. To achieve this, `blank` parameters to field definitions should always be the same as the `null` parameter, e.g. either `null=True, blank=True` or `null=False, blank=False`, the latter being the default values for both fields, which can therefore be omitted.

### Commit messages

All commits are labelled with the issue they are being done under. This ensures that we don't do work that is not tracked, and history of why every change is made is maintained. Most front end and back end work is tracked by issues in their respective repositories, in which case the commit message should start with "Issue #N", e.g. "Issue #13". Occasionally, front end work may be tracked under backend issues, in which case each commits message should start with "Issue pg-irc/pathways-backend#13".

## Change log

Changes that are made in each release are tracked following [Expo's](https://github.com/expo/expo/blob/master/CHANGELOG.md) procedure.

- changelog is updated with every PR that affects functionality.
- a new heading is added to the changelog as part of every PR that bumps version strings.
