from pyspark.sql import SparkSession
from pyspark.sql.functions import when
from pyspark.sql import DataFrame
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

pg_host = os.getenv("pg_host")
pg_port = os.getenv("pg_port")
pg_database = os.getenv("pg_database")
pg_user = os.getenv("pg_user")
pg_password = os.getenv("pg_password")
pg_table = os.getenv("pg_table")

mongo_uri = os.getenv("mongo_uri")
database_name = os.getenv("database_name")
collection_name = os.getenv("collection_name")

def create_spark_session():
    print("Creating Spark session...")
    return SparkSession.builder \
        .appName("PostgreSQL to MongoDB with PySpark") \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.2.5") \
        .getOrCreate()

def fetch_postgresql_data(spark: SparkSession) -> DataFrame:
    print("Fetching data from PostgreSQL...")
    db_url = f"jdbc:postgresql://{pg_host}:{pg_port}/{pg_database}"
    db_properties = {
        "user": pg_user,
        "password": pg_password,
        "driver": "org.postgresql.Driver"
    }

    query = f"(SELECT empid, firstname, lastname, title, ademail, employeestatus, employeetype, department, division, gendercode FROM {pg_table}) as tmp"
    df = spark.read.jdbc(url=db_url, table=query, properties=db_properties)
    print("Data fetched successfully.")
    return df

def insert_into_mongodb(data: DataFrame):
    print("Inserting data into MongoDB...")
    mongo_client = MongoClient(mongo_uri)
    mongo_db = mongo_client[database_name]
    mongo_collection = mongo_db[collection_name]
    data_dict = [row.asDict() for row in data.collect()]
    mongo_collection.insert_many(data_dict)
    print("Data inserted into MongoDB successfully.")
    mongo_client.close()

if __name__ == "__main__":
    spark = create_spark_session()
    print("created spark session.")
    pg_data_df = fetch_postgresql_data(spark)
    insert_into_mongodb(pg_data_df)
    spark.stop()
