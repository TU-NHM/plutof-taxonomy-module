PlutoF Taxonomy Module
============

Database and web service for managing multiple biological classifications.

## Requirements
* Make sure your [SSH keys](https://help.github.com/articles/generating-ssh-keys) are set up properly for GitHub.
* [pip](http://www.pip-installer.org/en/latest/)
* [elasticsearch](http://www.elasticsearch.org/overview/elkdownloads/)
* [PostgreSQL 9.1](http://www.postgresql.org/download/)

## Setup

## Clone
Clone the repository
```console
git clone git@github.com:TU-NHM/plutof-taxonomy-module.git
cd plutof-taxonomy-module
```

### Virtualenv
Create a virtualenv and *activate* it
```console
virtualenv env
source env/bin/activate
```

### Additional configuration (OS X)
Add paths to PostgreSQL installation and ElasticSearch folder into `~/.bash_profile`. For example (your paths may differ):
```console
PATH="$PATH:/Applications/Postgres.app/Contents/Versions/9.3/bin"
PATH="~/Documents/plutof/elasticsearch-1.1.0/bin:$PATH"
export PATH
```

Restart the terminal application for these changes to take effect. Activate the virtual environment as before.


### Database
Create a new PostgreSQL database `taxonomy` with username `taxonomy` and password `taxonomy`

### Install script
Run the install script
```console
make install
```

Add application superuser
```console
psql -U taxonomy
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (md5('pass'), NOW(), true, 'admin', '', '', '', true, true, NOW());
\q
```

Load aouth2 client (for data import)
```console
python manage.py loaddata apps/taxonomy/fixtures/oauth2_client.json
```

Import test tree
```console
make test-tree
```

## Tests
Run tests
```console
make test
```

## Server
Start Elasticsearch.
```console
elasticsearch
```

Run the development server
```console
make server
```

## Creating search indexes ([Haystack](http://django-haystack.readthedocs.org/en/latest/toc.html))

1. For creating an index use ```./manage.py rebuild_index```

2. For updating existing index use ```./manage.py update_index```
