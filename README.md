## About

A web page that generates statistics and graphs for a family game called Møkkis, which is a 6-athlon card game.

The web page is created using the python web framework Django, which generates jQuery Mobile pages. It also contains small amounts of custom JavaScript code, mostly to generate graphs with jqPlot (http://www.jqplot.com/).

The project is hosted on Google App Engine Standard Environment.

Find it here: https://mokstats.appspot.com/


## Get started

1. Install Python 3.13
2. Setup python env
     ``` powershell
     cd backend
     pip install poetry
     poetry sync
     ```
3. Setup database
   - Install Docker Desktop
   - Start docker container
     ``` powershell
     docker run --name mokstats-postgres -p 5432:5432 -e POSTGRES_USER=mokstats -e POSTGRES_PASSWORD=mokstats -e POSTGRES_DB=mokstats -d postgres:17
     ```
   - Migrate and populate database
     ``` powershell
     cd backend
     poetry shell
     python manage.py migrate
     python manage.py createcachetable
     ```
4. (Verify) Run tests `pytest .`
5. (Verify) Run lints: `.\lint.ps1`
6. (Optional) Setup pre-commit: `cp pre-commit.sh .git/hooks/pre-commit`


## Development tips

**Populate data from prod**

Run the content of `populate.sql` in a console connected to the database.

**Make an admin**

1. `python manage.py createsuperuser --username admin --email foo@foo.foo`
2. Test it by going to http://127.0.0.1:8000/admin

**Sync dependencies**

- `poetry update --sync`

**Run linters**

- `.\lints.ps1`


## Production interaction

**Configure secrets**

https://console.cloud.google.com/security/secret-manager/secret/PROD_ENV/versions?inv=1&invt=Abz9dA&project=mokstats

**Deploy with GitHub action**

Deploy can be manually triggered through a GitHub action. Se `.github/workflows/deploy.yml`.

**Check deployed files to app engine**

1. Find latest version here: https://console.cloud.google.com/appengine/versions?serviceId=default&hl=en&project=mokstats
2. `gcloud app versions describe --service=default "20250613t004846"`
