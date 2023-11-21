import pyodbc
import pandas as pd


def connect_to_mssql(server, database, username, password):
    try:
        # Create a connection string
        connection_string = f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

        # Establish a connection
        connection = pyodbc.connect(connection_string)

        return connection
    except Exception as e:
        print(f"Error connecting to MSSQL: {e}")
        return None


def execute_query(connection, query):
    try:
        # Create a cursor from the connection
        cursor = connection.cursor()

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the result set
        rows = cursor.fetchall()

        # Return the result
        return rows

    except Exception as e:
        print(f"Error executing query: {e}")
        return None

    finally:
        # Close the cursor
        cursor.close()


def export_to_excel(data, excel_filename):
    try:
        # Create a pandas DataFrame from the data
        df = pd.DataFrame(data)

        # Export to Excel
        df.to_excel(excel_filename, index=False)
        print(f"Data exported to {excel_filename}")

    except Exception as e:
        print(f"Error exporting to Excel: {e}")


if __name__ == "__main__":
    # Connection parameters
    server = "localhost"
    database = "MnrAccDB001"
    username = "sa"
    password = "123"

    # Connect to MSSQL
    connection = connect_to_mssql(server, database, username, password)

    if connection:
        # Get a list of tables
        tables_query = """
        SELECT table_name = t.name
        FROM sys.tables t
        INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
        ORDER BY t.name;
        """
        tables = execute_query(connection, tables_query)

        # Get table details
        table_details = []
        for table in tables:
            table_name = table[0]

            # Get columns in the table
            columns_query = f"EXEC sp_columns '{table_name}'"
            columns = execute_query(connection, columns_query)

            # Get foreign keys for the table
            foreign_keys_query = f"""
            SELECT 
                fk.name AS FK_name,
                tp.name AS parent_table,
                ref.name AS referenced_table
            FROM sys.foreign_keys fk
            INNER JOIN sys.tables tp ON fk.parent_object_id = tp.object_id
            INNER JOIN sys.tables ref ON fk.referenced_object_id = ref.object_id
            WHERE tp.name = '{table_name}' OR ref.name = '{table_name}';
            """
            foreign_keys = execute_query(connection, foreign_keys_query)

            # Append table details to the list
            table_details.append({
                'Table Name': table_name,
                'Columns': columns,
                'Foreign Keys': foreign_keys
            })

        # Export table details to Excel
        export_to_excel(table_details, 'database_details.xlsx')

        # Close the connection
        connection.close()
    else:
        print("Unable to connect to MSSQL.")
