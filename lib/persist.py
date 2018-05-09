import sqlalchemy
import pymysql
import pandas as pd

from settings import mysql_connect_str

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey


def get_db_engine():
    return create_engine(mysql_connect_str)


def sql_to_df(sql):
    engine = get_db_engine()
    resultProxy = engine.execute(sql)
    res = resultProxy.fetchall()
    return pd.DataFrame(res)

