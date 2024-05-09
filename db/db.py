import mysql.connector
import connect as connect

dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

def query(queryString):
    connection = getCursor()
    connection.execute(queryString)
    result = connection.fetchall()
    connection.close()
    return result

def queryOneResult(queryString):
    connection = getCursor()
    connection.execute(queryString)
    result = connection.fetchone()
    connection.close()
    return result


def querywithLastID(queryString):
    connection = getCursor()
    connection.execute(queryString)
    id = connection.lastrowid
    connection.close()
    return id