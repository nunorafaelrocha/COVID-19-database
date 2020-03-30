import csv

from functools import reduce
from os import listdir
from os.path import isfile, join
from slugify import slugify

# data source directory
data_source_repo = "/tmp/COVID-19"

# data types
types = ["confirmed", "deaths", "recovered"]

# slug util
def slug(text):
    return slugify(text.lower(), separator="_")

# Generate time series SQL file to create tables and import data from csv files.
def time_series(file):
    for name in types:
        table_name = "time_series_covid19_" + name
        file_name = data_source_repo + "/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_" + name + "_global.csv"

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

    daily_reports_dir = data_source_repo + "/csse_covid_19_data/csse_covid_19_daily_reports"

    for report_file in listdir(daily_reports_dir):
        if not report_file in [".gitignore", "README.md"]:
            report_file_location = daily_reports_dir + "/" + report_file

            with open(report_file_location, "r") as report:
                reader = csv.reader(report)
                original_columns = next(reader)

                day = report_file.replace(".csv", "")

                tmp_columns=" text , ".join(map(slug, original_columns)) + " text"

                file.write("""
                    CREATE TABLE {table_name}_temp ({tmp_columns});

                    COPY {table_name}_temp FROM '{report_file_location}' delimiter ',' CSV HEADER;

                    INSERT INTO {table_name} (day, province_state, country_region, confirmed, deaths, recovered)
                    SELECT '{day}', province_state, country_region, confirmed::INTEGER, deaths::INTEGER, recovered::INTEGER
                    FROM {table_name}_temp;

                    DROP TABLE {table_name}_temp;
                    """.format(table_name=table_name, day=day, tmp_columns=tmp_columns, report_file_location=report_file_location))

with open("/tmp/initdb.sql", "a+") as initdb:
    time_series(initdb)
    daily_reports(initdb)

    initdb.close()
