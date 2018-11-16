![POLITICO](https://rawgithub.com/The-Politico/src/master/images/logo/badge.png)

# politico-civic-ap-loader

Get live results from the AP Elections API, the POLITICO way.

### Quick disclaimer

This app is tailored to how POLITICO publishes election results, which might make it less plug-and-play than the rest of the POLITICO Civic project. The live results script filters down the AP Elections API response to just vote tallies and identifiers, due to how POLITICO publishes election results. It also assumes a directory structure when putting results onto Amazon S3. 

### Quickstart

1. Ensure `jq` is installed on your machine. On Mac OS X:

```
$ brew install jq
```

On Ubuntu:

```
$ sudo apt-get install jq
```

2. Install the app.

  ```
  $ pip install politico-civic-ap-loader
  ```

3. Add the app to your Django project and configure settings.

  ```python
  INSTALLED_APPS = [
      # ...
      'rest_framework',
      'entity',
      'geography',
      'government',
      'election',
      'vote',
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


  # bots
  CIVIC_SLACK_TOKEN = os.getenv("SLACK_TOKEN")
  CIVIC_SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
  CIVIC_TWITTER_CONSUMER_KEY = os.getenv("CIVIC_TWITTER_CONSUMER_KEY")
  CIVIC_TWITTER_CONSUMER_SECRET = os.getenv("CIVIC_TWITTER_CONSUMER_SECRET")
  CIVIC_TWITTER_ACCESS_TOKEN_KEY = os.getenv("CIVIC_TWITTER_ACCESS_TOKEN_KEY")
  CIVIC_TWITTER_ACCESS_TOKEN_SECRET = os.getenv(
      "CIVIC_TWITTER_ACCESS_TOKEN_SECRET"
  )

  ```

### Bootstrapping your database

1. Ensure `PROPUBLICA_CONGRESS_API_KEY` and `AP_API_KEY` is exported into your environment. If you don't have an API key for the ProPublica Congress API, you can request one [here](https://www.propublica.org/datastore/api/propublica-congress-api). For an AP Elections API key, [contact the Associated Press](https://developer.ap.org/ap-elections-api/).

2. Bootstrap the database.

```
$ python manage.py bootstrap_loader
```

### Publishing election results

##### Initialize

To initialize your database for a particular election date, run

```
$ python manage.py initialize_election_date <YYYY-MM-DD>
```

This will hydrate all of your upstream models with election data from the AP Elections API for that election date.

##### Live results

AP Loader comes with a daemonized process for publishing election results to Amazon S3. It takes two required arguments: an election date, and a level for results (`state` or `county`). You can also hit AP's test endpoint with the `--test` argument. For example, to get test state-level results:

```
$ python manage.py get_results 2018-11-06 state --test
```

##### Update database

There is another, separate daemonized process for getting the most recent vote tallies into the database. If you have Twitter and Slack bots configured in your environment, this will also handle posting new calls to Twitter and Slack.

```
$ python manage.py reup_to_db 2018-11-06 state
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