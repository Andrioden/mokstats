A web page that generates statistics and graphs for our traditional cabin game Møkkis, which is a 6athlon card game.

The web page is created using the python web framework Django, which generates jQuery Mobile pages. It also contains small amounts of custom JavaScript code, mostly to generate graphs with jqPlot (http://www.jqplot.com/).

The project is hosted on Google App Engine Standard Environment, and has related helperscripts and config.


## Development

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
