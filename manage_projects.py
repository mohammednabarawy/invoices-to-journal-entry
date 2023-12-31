from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QInputDialog
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sqlite3


class ManageProjects(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('projects.db')  # Initialize conn here
        self.init_ui()
        self.projects = self.get_projects_from_db()
        self.current_project_index = 0
        self.display_current_project()

    def init_ui(self):
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Manage Projects')
        self.setStyleSheet("background-color: #f0f0f0; font-size: 14px;")

        # Table for displaying projects
        self.project_table = QTableWidget(self)
        self.project_table.setColumnCount(5)
        self.project_table.setHorizontalHeaderLabels(
            ['Project Name', 'Debit Account', 'VAT Account', 'Credit Account', 'Cost Center'])
        self.project_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.project_table.itemSelectionChanged.connect(
            self.update_selected_project)
        self.display_projects_table()

        # Buttons for actions
        self.add_button = QPushButton('Add')
        self.save_button = QPushButton('Save Changes')
        self.delete_button = QPushButton('Delete')

        # Button connections
        self.add_button.clicked.connect(self.add_project)
        self.save_button.clicked.connect(self.save_changes_to_db)
        self.delete_button.clicked.connect(self.delete_project)

        # Apply styles to buttons
        self.add_button.setStyleSheet(
            "background-color: #4caf50; color: #ffffff;")
        self.save_button.setStyleSheet(
            "background-color: #2196f3; color: #ffffff;")
        self.delete_button.setStyleSheet(
            "background-color: #f44336; color: #ffffff;")

        # Add icons to buttons
        self.add_button.setIcon(QIcon('add_icon.png'))
        self.save_button.setIcon(QIcon('save_icon.png'))
        self.delete_button.setIcon(QIcon('delete_icon.png'))

        # Vertical layout for the table and buttons
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.project_table)
        main_layout.addWidget(self.add_button)
        main_layout.addWidget(self.save_button)
        main_layout.addWidget(self.delete_button)

        self.setLayout(main_layout)
        # Adjust column widths based on content
        for col in range(self.project_table.columnCount()):
            self.project_table.resizeColumnToContents(col)

        # Ensure the UI fits all columns
        table_width = self.project_table.horizontalHeader().length() + \
            20  # Add a margin
        self.setFixedWidth(max(table_width, 800))  # Set minimum width to 800

    def display_projects_table(self):
        self.projects = self.get_projects_from_db()  # Initialize projects here
        self.project_table.setRowCount(len(self.projects))
        for row, project in enumerate(self.projects):
            for col, value in enumerate(project):
                item = QTableWidgetItem(str(value))
                self.project_table.setItem(row, col, item)

    def update_selected_project(self):
        selected_row = self.project_table.currentRow()
        if 0 <= selected_row < len(self.projects):
            self.current_project_index = selected_row
            self.display_current_project()

    def get_projects_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects")
        self.projects = cursor.fetchall()
        return self.projects

    def display_current_project(self):
        if self.projects:
            project = self.projects[self.current_project_index]
            self.project_table.selectRow(self.current_project_index)

    def add_project(self):
        # Add a new row to the table
        self.project_table.setRowCount(self.project_table.rowCount() + 1)

    def save_changes_to_db(self):
        try:
            cursor = self.conn.cursor()
            for row in range(self.project_table.rowCount()):
                project_name = self.project_table.item(row, 0).text()
                debit_account = self.project_table.item(row, 1).text()
                vat_account = self.project_table.item(row, 2).text()
                credit_account = self.project_table.item(row, 3).text()
                cost_center = self.project_table.item(row, 4).text()

                if not project_name:  # Skip empty rows
                    continue

                cursor.execute('''
                    INSERT OR REPLACE INTO projects
                    (project_name, debit_account, vat_account, credit_account, cost_center)
                    VALUES (?, ?, ?, ?, ?)
                ''', (project_name, debit_account, vat_account, credit_account, cost_center))

            self.conn.commit()
            self.get_projects_from_db()
            self.show_message_box("Changes saved successfully.")
        except Exception as e:
            self.show_message_box(f"Failed to save changes: {e}")

    def delete_project(self):
        selected_row = self.project_table.currentRow()
        if 0 <= selected_row < len(self.projects):
            project_name = self.project_table.item(selected_row, 0).text()
            cursor = self.conn.cursor()
            cursor.execute(
                'DELETE FROM projects WHERE project_name = ?', (project_name,))
            self.conn.commit()
            self.get_projects_from_db()
            self.display_projects_table()
            self.show_message_box("Row deleted successfully.")
        else:
            self.show_message_box("Please select a row to delete.")

    def show_message_box(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Message")
        msg.exec_()


# Example of usage
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ManageProjects()
    window.show()
    sys.exit(app.exec_())
