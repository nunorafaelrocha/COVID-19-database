import csv

from functools import reduce
from os import listdir
from os.path import isfile, join
from slugify import slugify

# data source directory
data_source_repo = "/tmp/COVID-19"

# data types
types = ["Confirmed", "Deaths", "Recovered"]

# slug util
def slug(text):
    return slugify(text, separator="_")

# Generate time series SQL file to create tables and import data from csv files.
def time_series(file):
    for name in types:
        table_name = "time_series_19_covid_" + name
        file_name = data_source_repo + "/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-" + name + ".csv"

        with open(file_name, "r") as f:
            reader = csv.reader(f)
            header=next(reader)

            def create_day_column(acc, day):
                return acc + "\" int, \"" + day

            days_columns = "\"" + reduce(create_day_column, header[4:]) + "\" int";

            file.write("""
                DROP TABLE IF EXISTS {table_name};\n

                CREATE TABLE {table_name} (
                province_state text,
                country_region text,
                lat text,
                long text,
                {days_columns}
                );

                COPY {table_name} FROM '{file_name}' delimiter ',' CSV HEADER;
                \n
            """.format(table_name=table_name, file_name=file_name, days_columns=days_columns))

# Generate daily reports SQL file to create tables and import data from csv files.
def daily_reports(file):
    table_name="daily_reports_19_covid"
    daily_reports_dir = data_source_repo + "/csse_covid_19_data/csse_covid_19_daily_reports"

    file.write("""
        DROP TABLE IF EXISTS {table_name};\n

        CREATE TABLE {table_name} (
        province_state text,
        country_region text,
        day date,
        confirmed int,
        deaths int,
        recovered int);
        \n
    """.format(table_name=table_name));

    file_name = data_source_repo + "/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
    with open(file_name, "r") as report:
        reader = csv.reader(report)
        columns=next(reader)

        for column in columns[5:]:
            file.write("""
                INSERT INTO daily_reports_19_covid (province_state, country_region, day, confirmed, deaths, recovered)
                SELECT
                    tc.province_state,
                    tc.country_region,
                    '{column}' as day,
                    tc."{column}" as confirmed,
                    td."{column}" as deaths,
                    tr."{column}" as recovered
                FROM time_series_19_covid_Confirmed tc
                LEFT JOIN time_series_19_covid_Deaths td ON tc.province_state = td.province_state AND tc.country_region = td.country_region
                LEFT JOIN time_series_19_covid_Recovered tr ON tc.province_state = tr.province_state AND tc.country_region = tr.country_region;
                \n
                """.format(column=column))

with open("/tmp/initdb.sql", "a+") as initdb:
    time_series(initdb)
    daily_reports(initdb)

    initdb.close()
