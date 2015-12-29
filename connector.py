import sqlite3

def open_conn(database):
    return sqlite3.connect(database) 

