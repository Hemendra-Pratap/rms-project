import sqlite3

# Path to your .sql file
sql_file_path = 'rms.sql'

# Path to your database file
db_file = 'rms.db'

# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Read the SQL file
with open(sql_file_path, 'r', encoding='utf-8') as f:
    sql_script = f.read()

# Execute the SQL script
try:
    cursor.executescript(sql_script)
    conn.commit()
    print("Database initialized successfully from rms.sql.")
except Exception as e:
    print("An error occurred:", e)
finally:
    conn.close()
