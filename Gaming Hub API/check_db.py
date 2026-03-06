import sqlite3
import os

if os.path.exists('gaminghub.db'):
    conn = sqlite3.connect('gaminghub.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print('Tables:', tables)
    for table in tables:
        cursor.execute(f'PRAGMA table_info({table[0]})')
        cols = cursor.fetchall()
        print(f'{table[0]} columns:', cols)
    conn.close()
else:
    print('gaminghub.db does not exist')
