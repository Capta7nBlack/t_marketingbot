import sqlite3


def open():
    conn_func = sqlite3.connect("modules/database.db")
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
             'photo_path TEXT,'
             'post_text TEXT,'
             'post_date TEXT,'
             'post_time TEXT,'
             'cancelled INTEGER DEFAULT 0,'
             'hidden INTEGER DEFAULT 0, '
             'kaspi_path TEXT,'
             'username TEXT'
             ')'
             )
    close(conn,curr)


def new_write(user_id, username, photo_path, post_text, post_date, post_time, kaspi_path ):
    conn, curr = open()
    curr.execute('INSERT INTO adds (user_id, username, photo_path, post_text, post_date, post_time, kaspi_path ) VALUES (?,?,?,?,?,?,?)', (user_id, username, photo_path, post_text, post_date, post_time, kaspi_path))
    close(conn,curr)


def show_all(user_id, min_date=None, max_date=None):
    conn, curr = open()
    query = 'SELECT photo_path, post_text, post_date, post_time, kaspi_path FROM adds WHERE user_id = ? AND hidden = ?;'
    hidden = 0
    curr.execute(query,(user_id, hidden))
    data = curr.fetchall()
    return data


def show_between(min_date, max_date):
    conn, curr = open()
    query = '''
    SELECT photo_path, post_text, post_date, post_time, kaspi_path 
    FROM adds 
    WHERE post_date BETWEEN ? AND ?;
            '''    
    hidden = 0
    curr.execute(query,(min_date, max_date))
    data = curr.fetchall()
    return data







