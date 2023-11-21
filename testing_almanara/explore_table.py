import pyodbc

# Replace these values with your actual database connection details
server = "localhost"
database = "MnrAccDB001"
username = "sa"
password = "123"

# Define the table name
table_name = 'mnrAcc'

# Create a connection string
connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# Establish a connection
connection = pyodbc.connect(connection_string)

# Create a cursor to execute SQL queries
cursor = connection.cursor()

try:
    # Get column information for the specified table
    columns_query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'"
    cursor.execute(columns_query)
    columns = [column[0] for column in cursor.fetchall()]

    # Print column names
    print(f"Columns in {table_name} table: {columns}")

    # Sample query to retrieve data (adjust as needed)
    sample_query = f"SELECT TOP 5 * FROM {table_name}"
    cursor.execute(sample_query)

    # Print sample data
    for row in cursor.fetchall():
        print(row)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the cursor and connection
    cursor.close()
    connection.close()
