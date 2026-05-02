import sqlite3
conn = sqlite3.connect('mindcare.db')
tables = conn.execute("SELECT name, sql FROM sqlite_master WHERE type='table'").fetchall()
for name, sql in tables:
    print('=' * 50)
    print('TABLE:', name.upper())
    print('=' * 50)
    print(sql)
    print()
conn.close()
