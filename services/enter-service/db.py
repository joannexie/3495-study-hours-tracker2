import os
import pymysql

def get_conn():
    return pymysql.connect(
        host=os.environ.get("MYSQL_HOST", "mysql"),
        port=int(os.environ.get("MYSQL_PORT", "3308")),
        user=os.environ.get("MYSQL_USER", "appuser"),
        password=os.environ.get("MYSQL_PASSWORD", "apppassword"),
        database=os.environ.get("MYSQL_DB", "studytracker"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
