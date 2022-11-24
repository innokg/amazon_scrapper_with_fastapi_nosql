"""
Module for connecting to the Cassandra DB
"""

import os
import pathlib

from dotenv import load_dotenv

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine.connection import register_connection, set_default_connection
from . import config


settings = config.get_settings()

load_dotenv()
ASTRA_DB_CLIENT_ID = settings.db_client_id
ASTRA_DB_CLIENT_SECRET = settings.db_client_secret

BASE_DIR = pathlib.Path(__file__).parent  # Access the zip folder
CLUSTER_BUNDLE = str(BASE_DIR / "ignored" / "connect.zip")


def get_cluster():
    cloud_config = {'secure_connect_bundle': CLUSTER_BUNDLE}
    auth_provider = PlainTextAuthProvider(ASTRA_DB_CLIENT_ID, ASTRA_DB_CLIENT_SECRET)  # connected to the DB
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    return cluster


def get_session():
    cluster = get_cluster()
    session = cluster.connect()
    register_connection(str(session), session=session)  # register the connection
    set_default_connection(str(session))  # setting default connection
    return session

# session = get_session()
# if row := session.execute("select release_version from system.local").one():
#     print(row[0])
# else:
#     print("An error occurred.")
