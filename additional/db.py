import sqlite3

def open():
    conn_func = sqlite3.connect("database.db")
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
             'cancelled INTEGER,'
             'temporary INTEGER, '
             'kaspi TEXT'
             ')'
             )

    close(conn,curr)

def temporary_delete(user_id):
    conn, curr = open()
    curr.execute('DELETE FROM adds WHERE user_id = ? AND temporary = ?', (user_id, 1))
    close(conn,curr)


def temporary_write(user_id, photo_path, post_text ):
    conn, curr = open()
    curr.execute('INSERT INTO adds (photo_path, post_text,user_id, temporary) VALUES (?,?,?,?)', (photo_path, post_text, user_id, 1))
    close(conn,curr)

def temporary_write_date(user_id, date):
    conn, curr = open()
    curr.execute('UPDATE adds SET post_date = ? WHERE temporary = ? AND user_id = ?', (date, 1, user_id))
    close(conn,curr)



def temporary_read(user_id):
    conn, curr = open()
    curr.execute('SELECT photo_path, post_text, post_date FROM adds WHERE temporary = ? AND user_id = ?', (1, user_id))
    data = curr.fetchone()
    close(conn,curr)
    return data
    



