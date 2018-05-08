import sqlalchemy
import pymysql
import pandas as pd

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey


def get_db_engine(connect_str):
    return create_engine(connect_str)


def sql_to_df(sql):
    engine = get_db_engine('mysql+pymysql://<username>:<password>@<host>/<dbname>[?<options>]')
