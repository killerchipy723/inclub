from dbutils.pooled_db import PooledDB
import pymysql

pool = PooledDB(
    creator=pymysql,
    maxconnections=10,
    host="localhost",
    user="root",
    password="inclub123",
    database="inclub_offline",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=False
)

def getConnection():
    return pool.connection()
