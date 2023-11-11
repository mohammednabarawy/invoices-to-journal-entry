import sqlite3

conn = sqlite3.connect('projects.db')
cursor = conn.cursor()

# Create a table for expenses and their associated accounts, referencing the project
cursor.execute('''
    CREATE TABLE IF NOT EXISTS project_expenses (
        id INTEGER PRIMARY KEY,
        project_name TEXT,
        expense_name TEXT,
        expense_account TEXT,
        FOREIGN KEY (project_name) REFERENCES projects(project_name)
    )
''')
conn.commit()
