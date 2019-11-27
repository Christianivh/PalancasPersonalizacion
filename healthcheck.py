import pandas as pd
import os
import sys
import inspect
import boto3

from google.cloud import bigquery
from google.cloud import bigquery_storage_v1beta1
from google.oauth2 import service_account
from google.auth.exceptions import *
from sqlalchemy import create_engine

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)


def download_pickle(file_name, bucket, folder):
    boto3.Session().resource('s3').Bucket(bucket).Object(os.path.join(folder, file_name)).download_file(file_name)


def check_redshift(engine):
    """
    check_redshift: validate
    :param engine:
    :return:
    """
    try:
        conn = create_engine(engine)
        query = "SELECT TOP 1 codstatus FROM fnc_analitico.dwh_dstatus"
        df = pd.read_sql_query(query, conn)
        print("redshift: successful")
    except:
        print("redshift: error connection: ", sys.exc_info()[0])


def check_big_query(ArchivoJson):
    try:
        credentials = service_account.Credentials.from_service_account_file(ArchivoJson)
        print("cred")
        scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
        print("scoped_credentials")
        bqclient = bigquery.Client(credentials=scoped_credentials, project="firm-aviary-195016")
        print("bqclient")
        bqstorageclient = bigquery_storage_v1beta1.BigQueryStorageClient(credentials=scoped_credentials)
        print("bqstorageclient")
        query = "SELECT totals.timeOnSite AS Tiempo, FullVisitorID FROM `firm-aviary-195016.81564101.ga_sessions_*`WHERE _TABLE_SUFFIX='20190101'"
        print("query")
        dataframe = (bqclient.query(query).result().to_dataframe(bqstorage_client=bqstorageclient))
        print("bigquery: successful")
    except ImportError as error:
        print("Import error: ", error)
    except TransportError as error:
        print("Import error: ", error)
    except:
        print("Unexpected error: ", sys.exc_info()[0])


if __name__ == '__main__':
    bucket2 = os.environ['BUCKET_JSON']
    folder = os.environ['FOLDER']
    ArchivoJson = os.environ['ArchivoJson']
    engine = os.environ['RedShift']
    download_pickle(ArchivoJson, bucket2, folder)
    check_redshift(engine)
    check_big_query(ArchivoJson)
