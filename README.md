![POLITICO](https://rawgithub.com/The-Politico/src/master/images/logo/badge.png)

# politico-civic-ap-loader

### Quickstart

1. Install the app.

  ```
  $ pip install politico-civic-ap-loader
  ```

2. Add the app to your Django project and configure settings.

  ```python
  INSTALLED_APPS = [
      # ...
      'rest_framework',
      'aploader',
  ]

  #########################
  # aploader settings

  APLOADER_SECRET_KEY = ''
  APLOADER_AWS_ACCESS_KEY_ID = ''
  APLOADER_AWS_SECRET_ACCESS_KEY = ''
  APLOADER_AWS_REGION = ''
  APLOADER_AWS_S3_BUCKET = ''
  APLOADER_CLOUDFRONT_ALTERNATE_DOMAIN = ''
  APLOADER_S3_UPLOAD_ROOT = ''
  ```

### Developing

##### Running a development server

Developing python files? Move into example directory and run the development server with pipenv.

  ```
  $ cd example
  $ pipenv run python manage.py runserver
  ```

Developing static assets? Move into the pluggable app's staticapp directory and start the node development server, which will automatically proxy Django's development server.

  ```
  $ cd aploader/staticapp
  $ gulp
  ```

Want to not worry about it? Use the shortcut make command.

  ```
  $ make dev
  ```

##### Setting up a PostgreSQL database

1. Run the make command to setup a fresh database.

  ```
  $ make database
  ```

2. Add a connection URL to the `.env` file.

  ```
  DATABASE_URL="postgres://localhost:5432/aploader"
  ```

3. Run migrations from the example app.

  ```
  $ cd example
  $ pipenv run python manage.py migrate
  ```

4. Bootstrap initial data (this will take about 20 minutes)
  
  ```
  $ pipenv run python manage.py bootstrap_loader
  ```

##### Getting results to S3

```
$ pipenv run python manage.py get_results <ELECTION_DATE> <LEVEL> --test
```

##### Reupload results to database

```
$ pipenv run python manage.py reup_to_db <ELECTION_DATE>
```