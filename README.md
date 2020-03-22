# 🦠 COVID-19-database

A ready to use PostgreSQL database that contains COVID-19 data from [Johns Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19).

## ⚡️Quick start

```sh
docker run -e POSTGRES_HOST_AUTH_METHOD=trust -p5432:5432 nunorafaelrocha/covid19-postgres:latest
```

This docker images is based on [Postgres Official docker image](https://hub.docker.com/_/postgres/). See Postgres [documentation](https://hub.docker.com/_/postgres/) to check all options.

## 💾 Datasets

### Daily reports (daily_reports_19_covid)

Contains daily case reports.

- daily_reports_19_covid

### Time series summary (time_series_19_covid)

Contains daily time series summary tables, including confirmed, deaths and recovered. All data are from the daily case report.

- time_series_19_covid_confirmed
- time_series_19_covid_deaths
- time_series_19_covid_recovered

## ♻️ Fetch new data

To fetch the latest data, run the following command:

```sh
docker exec -it <CONTAINER_ID> ./setup.sh
```

Example with `docker ps` and `awk`

```sh
docker exec -it $(docker ps | grep "covid19-postgres" | awk '{ print $1 }') ./setup.sh
```

**Note:** The data is updated once a day around 23:59 UTC.
