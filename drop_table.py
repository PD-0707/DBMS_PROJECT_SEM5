import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute('DROP TABLE IF EXISTS CHAT')

conn.commit()
conn.close()

print(" table dropped successfully!")
