# Pathways backend

This repository contains the server for providing access to data about services for refugees and immigrants to BC.

We can import and serve up read-only services data from the BC-211 dataset, using the [HSDS](http://openreferral.readthedocs.io/en/latest/hsds/reference/) data format and [HSDA API](http://docs.openreferral.org/en/latest/) format.

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
pip install -r requirements/local.txt
python -m spacy download en
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
DJANGO_AWS_STORAGE_BUCKET_NAME=peacegeeks-pathways-static \
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

Import BC-211 data

```
python manage.py import_bc211_data ~/path/to/AIRSXML_2252_Export_20170109050136__211.xml

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
```

Then run the upgrade script for either local, rest or production environment, e.g.:

```
./utility/upgrade_packages.sh production
```

You will be prompted to decide which of the possible upgrades you will take (this is using [pur](https://pypi.python.org/pypi/pur) in interactive mode), the requirement files are updated and a new environment is created using the new packages for use in testing before the upgrades are committed.

## Getting started with Heroku

Create a Heroku instance with these environment variables:

* DATABASE_URL (managed by Heroku)
* DJANGO_AWS_STORAGE_BUCKET_NAME=peacegeeks-pathways-static
* DJANGO_SECRET_KEY
* DJANGO_SETTINGS_MODULE=config.settings.production

Update ALLOWED_HOSTS production settings to include the name of the heroku instance

To clear out the database content

```
% heroku restart
% heroku pg:reset DATABASE
```

To initialize the database schema

```
% heroku run ./manage.py migrate
```

To connect to the heroku instance over SSH:

```
heroku ps:exec
```

### Deployment on Heroku

To deploy on Heroku from an empty production database: First prepare the deployment
files locally using the `utility/prepare_deploy.sh` script. It should be called with three
arguments

  * Path to the XML file containing the BC211 data
  * Path to the folder containing the Newcomers Guide content
  * Path to the output file to generate, must end in `.json`

Upload the json file to AWS so that it can be accessed from Heroku. Then log into heroku
using `ps:exec`, set the environment variables including the correct DB URL

```
export DJANGO_SETTINGS_MODULE=config.settings.production
export DJANGO_SECRET_KEY='the key'
export DJANGO_AWS_STORAGE_BUCKET_NAME=peacegeeks-pathways-static
export DJANGO_MAILGUN_API_KEY='the key'
export MAILGUN_SENDER_DOMAIN='the domain'
export DATABASE_URL='the database url from heroku settings'
export DJANGO_READ_DOT_ENV_FILE=False
```

and load the data into the empty database
```
./manage.py reset_db
./manage.py migrate
wget https://path/to/amazon/s3/storage/deploy_data.json
./manage.py loaddata deploy_data.json
```

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

Certain content is translatable, using [django-parler](http://django-parler.readthedocs.io/). The *translation* module provides management commands to export translatable strings as POT files, and import their translations from PO files.

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

    ./manage.py import_newcomers_guide path/to/newcomers/guide/content

This produces a number of typescript files in the working directory. Move these files into the client
folder structure

    mv *.ts ../pathways-frontend/src/fixtures/newcomers_guide/

Build the client as normal, noting that the screen output contains the line `bin/buildFixtures.sh: Using Newcomers Guide fixtures` to indicate that the Newcomers' Guide content is being used.

## Development

### Null and django blank

Required string fields should never be null and never be the empty string. Optional string fields should never be the empty string. To achieve this, `blank` parameters to field definitions should always be the same as the `null` parameter, e.g. either `null=True, blank=True` or `null=False, blank=False`, the latter being the default values for both fields, which can therefore be omitted.

### Commit messages

All commits are labelled with the issue they are being done under. This ensures that we don't do work that is not tracked, and history of why every change is made is maintained. Most front end and back end work is tracked by issues in their respective repositories, in which case the commit message should start with "Issue #N", e.g. "Issue #13". Occasionally, front end work may be tracked under backend issues, in which case each commits message should start with "Issue pg-irc/pathways-backend#13".
