import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

with open('schema.sql', 'r') as f:
    schema_sql = f.read()

c.executescript(schema_sql)
conn.commit()
conn.close()

print("Tables created successfully!")
