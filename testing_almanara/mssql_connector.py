import pyodbc
import pandas as pd


def connect_to_mssql():
    try:
        # Connection parameters
        server = "localhost"
        database = "MnrAccDB001"
        username = "sa"
        password = "123"

        # Create a connection string
        connection_string = f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

        # Establish a connection
        connection = pyodbc.connect(connection_string)

        return connection
    except Exception as e:
        print(f"Error connecting to MSSQL: {e}")
        return None


def select_from_mnrentry(connection):
    try:
        # Create a cursor from the connection
        cursor = connection.cursor()

        # Execute a SELECT query on the "mnrentry" table
        cursor.execute("SELECT * FROM mnrentry")

        # Fetch all rows from the result set
        rows = cursor.fetchall()

        # Create a pandas DataFrame from the query result
        df = pd.DataFrame([tuple(row) for row in rows], columns=[
                          column[0] for column in cursor.description])

        # Print the result to the console
        print("Result from mnrentry table:")
        print(df)

        # Export the DataFrame to an Excel file
        df.to_excel("mnrentry_output.xlsx", index=False)

    except Exception as e:
        print(f"Error executing SELECT query: {e}")

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()


if __name__ == "__main__":
    # Connect to MSSQL
    connection = connect_to_mssql()

    if connection:
        # Select from mnrentry and print the result
        select_from_mnrentry(connection)
    else:
        print("Unable to connect to MSSQL.")
