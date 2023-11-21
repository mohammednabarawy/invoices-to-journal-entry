import sqlite3
import pyodbc

# Connect to the source SQL Server database
source_conn_str = (
    "DRIVER={SQL Server Native Client 11.0};"
    "SERVER=localhost;"
    "DATABASE=MnrAccDB001;"
    "UID=sa;"
    "PWD=123;"
)
source_conn = pyodbc.connect(source_conn_str)
source_cursor = source_conn.cursor()

# Connect to the destination SQLite database
destination_conn = sqlite3.connect('projects.db')
destination_cursor = destination_conn.cursor()

# Fetch data from the source table
source_cursor.execute('SELECT * FROM mnrAcc')
rows = source_cursor.fetchall()

# Get the column names
columns = [column[0] for column in source_cursor.description]

# Create the destination table in SQLite
create_table_query = f"CREATE TABLE IF NOT EXISTS mnrAcc ({', '.join(columns)})"
destination_cursor.execute(create_table_query)

# Insert data into the destination table
insert_query = f"INSERT INTO mnrAcc ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(columns))})"
destination_cursor.executemany(insert_query, rows)

# Commit the changes and close the connections
destination_conn.commit()
source_conn.close()
destination_conn.close()

print("Table copied successfully.")
