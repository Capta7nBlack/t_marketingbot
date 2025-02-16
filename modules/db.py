import sqlite3

import datetime

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import db_path, cleaner_days


def open():
    conn_func = sqlite3.connect(db_path)
    curr_func = conn_func.cursor()
    print("The db connection is opened")
    return conn_func, curr_func


def close(conn_func, curr_func):
    conn_func.commit()
    curr_func.close()
    conn_func.close()
    print("The db connection is closed")


def create():

    conn, curr = open()
    curr.execute('CREATE TABLE IF NOT EXISTS adds('
             'id INTEGER PRIMARY KEY,'
             'user_id INTEGER,'
             'input_photo_path TEXT,'
             'photo_path TEXT,'
             'post_text TEXT,'
             'post_date TEXT,'
             'post_time TEXT,'
             'kaspi_path TEXT,'
             'username TEXT'
             ')'
             )
    close(conn,curr)


def new_write(user_id, username,input_photo_path, photo_path, post_text, post_date, post_time, kaspi_path ):
    conn, curr = open()
    curr.execute('INSERT INTO adds (user_id, username,input_photo_path, photo_path, post_text, post_date, post_time, kaspi_path ) VALUES (?,?,?,?,?,?,?,?)',
                 (user_id, username, input_photo_path, photo_path, post_text, post_date, post_time, kaspi_path))
    close(conn,curr)


def show_all(user_id, min_date=None, max_date=None):
    conn, curr = open()
    query = 'SELECT photo_path, post_text, post_date, post_time, kaspi_path FROM adds WHERE user_id = ?;'
    curr.execute(query,(user_id,))
    data = curr.fetchall()
    return data


def show_between(min_date, max_date):
    conn, curr = open()
    query = '''
    SELECT photo_path, post_text, post_date, post_time, kaspi_path 
    FROM adds 
    WHERE post_date BETWEEN ? AND ?;
            '''    
    curr.execute(query,(min_date, max_date))
    data = curr.fetchall()
    return data


def fetch_and_clean_old_records():
    # Calculate the date threshold (half a year ago)
    older_than = (datetime.datetime.now() - datetime.timedelta(days=cleaner_days)).strftime("%Y-%m-%d")

    # Connect to SQLite database
    conn, cursor = open()

    # Fetch specified columns from rows older than half a year
    cursor.execute(f"""
        SELECT input_photo_path, photo_path, kaspi_path 
        FROM adds 
        WHERE post_date < ?
    """, (older_than,))
    
    old_records = cursor.fetchall()

    if old_records:
        print(f"Records older than {older_than}:")
        for record in old_records:
            print(record)
    else:
        print(f"No records older than {older_than}")
        
    # Delete rows older than half a year
    cursor.execute(f"""
        DELETE FROM adds
        WHERE post_date < ?
    """, (older_than,))
    
    # Commit changes and close connection
    close(conn, cursor)
    print(f"Deleted records in db older than {older_than} if they were present.")
    return old_records


def delete_actual_files(old_records):
    """Delete files from photo_path and kaspi_path in old_records."""

    for record in old_records:
        input_photo_path, photo_path, kaspi_path = record

        # Delete input_photo_path file if it exists
        if input_photo_path and os.path.exists(input_photo_path):
            try:
                os.remove(input_photo_path)
                print(f"Deleted: {input_photo_path}")
            except Exception as e:
                print(f"Error deleting {input_photo_path}: {e}")
        else:
            print(f"File not found: {input_photo_path}. Probably because input photos are constantly rewritten on top of each other. One user - one input photo saved in local, but in db each saved as a separate column.")
        
        # Delete photo_path file if it exists
        if photo_path and os.path.exists(photo_path):
            try:
                os.remove(photo_path)
                print(f"Deleted: {photo_path}")
            except Exception as e:
                print(f"Error deleting {photo_path}: {e}")
        else:
            print(f"File not found: {photo_path}")
        
        # Delete kaspi_path file if it exists
        if kaspi_path and os.path.exists(kaspi_path):
            try:
                os.remove(kaspi_path)
                print(f"Deleted: {kaspi_path}")
            except Exception as e:
                print(f"Error deleting {kaspi_path}: {e}")
        else:
            print(f"File not found: {kaspi_path}")

    if not old_records:
        print("No records from db to delete actual files")







