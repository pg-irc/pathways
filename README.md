# Pathways backend

This repository contains the server for providing access to data about services for refugees and immigrants to BC.

At this stage, our focus is on establishing the server architecture and testing frameworks for unit, integration and feature testing, continuous integration, logging, etc. The domain model is still that from a django turorial on polls, with a single one-to-many relationship from questions to choices. The plan is for future services to be built with the polls service as pattern, and the polls patter to be discarded. This will happen as our understanding of our domain improves.

## Getting started

Set up and activate a python v3 environment

```
python3 -m venv PW
source ./PW/bin/activate
```

Clone the repository:

```
git clone https://github.com/pg-irc/pathways-backend.git
cd pathways-backend/
```

Install required libraries in the python environment created above:

`pip install -r requirements.txt`

Create database tables -- note that we are using SqlLite for now, the plan is to deploy on Postgres:

`python manage.py migrate`

Create the django administration account:

`python manage.py createsuperuser`

Run the unit tests

`python manage.py test`

Start the API server

`python manage.py runserver`

You should now be able to access the server at http://127.0.0.1:8000/v1/. The Django admin tool is at http://127.0.0.1:8000/v1/admin/, and the question and choice entities are available at http://127.0.0.1:8000/v1/questions/ and http://127.0.0.1:8000/v1/questions/1/choices/.

## Development

### Null and django blank

Required string fields should never be null and never be the empty string. Optional string fields should never be the empty string. To achieve this, `blank` parameters to field definitions should always be the same as the `null` parameter, e.g. either `null=True, blank=True` or `null=False, blank=False`, the latter being the default values for both fields, which can therefore be omitted.

### Commit messages

All commits are labelled with the issue they are being done under. This ensures that we don't do work that is not tracked, and history of why every change is made is maintained. Most front end and back end work is tracked by issues in their respective repositories, in which case the commit message should start with "Issue #N", e.g. "Issue #13". Occasionally, front end work may be tracked under backend issues, in which case each commits message should start with "Issue pg-irc/pathways-backend#13".
