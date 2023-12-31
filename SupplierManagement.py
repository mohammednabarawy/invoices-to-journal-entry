from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QApplication, QHeaderView
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sqlite3


class SupplierManagement(QWidget):
    def __init__(self):
        super().__init__()

        # SQLite database connection
        self.conn = sqlite3.connect('projects.db')
        self.create_suppliers_table()

        # Initialize the UI
        self.init_ui()

        # Load existing suppliers from the database
        self.load_suppliers_from_db()

    def init_ui(self):
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Supplier Management')
        self.setStyleSheet("background-color: #f0f0f0; font-size: 14px;")

        # Table for displaying and editing supplier information
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            ['Supplier Name', 'VAT Number', 'Account Number'])
        self.table.setStyleSheet(
            "background-color: #ffffff; selection-background-color: #b3d9ff;")
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Buttons for adding and deleting rows
        self.add_row_button = QPushButton('Add Row')
        self.delete_row_button = QPushButton('Delete Row')
        self.save_button = QPushButton('Save Changes')

        self.add_row_button.setStyleSheet(
            "background-color: #4caf50; color: #ffffff;")
        self.delete_row_button.setStyleSheet(
            "background-color: #f44336; color: #ffffff;")
        self.save_button.setStyleSheet(
            "background-color: #2196f3; color: #ffffff;")

        self.add_row_button.setIcon(QIcon('add_icon.png'))
        self.delete_row_button.setIcon(QIcon('delete_icon.png'))
        self.save_button.setIcon(QIcon('save_icon.png'))

        self.add_row_button.clicked.connect(self.add_row)
        self.delete_row_button.clicked.connect(self.delete_row)
        self.save_button.clicked.connect(self.save_changes_to_db)

        # Vertical layout for the main window
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.add_row_button)
        main_layout.addWidget(self.delete_row_button)
        main_layout.addWidget(self.save_button)

        self.setLayout(main_layout)
        # Adjust column widths based on content
        for col in range(self.table.columnCount()):
            self.table.resizeColumnToContents(col)

        # Ensure the UI fits all columns
        table_width = self.table.horizontalHeader().length() + \
            20  # Add a margin
        self.setFixedWidth(max(table_width, 800))  # Set minimum width to 800

    def create_suppliers_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                name TEXT,
                vat_number TEXT,
                credit_account TEXT
            )
        ''')
        self.conn.commit()

    def load_suppliers_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM suppliers")
        rows = cursor.fetchall()

        # Populate the table with data from the database
        self.table.setRowCount(len(rows))
        for row_index, row_data in enumerate(rows):
            for col_index, col_value in enumerate(row_data):
                self.set_table_item(row_index, col_index, str(col_value))

    def add_row(self):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.clear_table_row(row_position)

    def delete_row(self):
        selected_row = self.table.currentRow()

        if selected_row == -1:
            self.show_message_box("Please select a row to delete.")
            return

        reply = QMessageBox.question(self, 'Delete Row', 'Are you sure you want to delete this row?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.table.removeRow(selected_row)
            self.delete_row_from_db(selected_row)

    def delete_row_from_db(self, row):
        cursor = self.conn.cursor()

        # Check if the row is not empty
        if self.table.item(row, 0) is not None:
            name = self.table.item(row, 0).text()
            vat_number = self.table.item(row, 1).text()
            credit_account = self.table.item(row, 2).text()

            cursor.execute("DELETE FROM suppliers WHERE name=? AND vat_number=? AND credit_account=?",
                           (name, vat_number, credit_account))

            self.conn.commit()

    def save_changes_to_db(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM suppliers")  # Clear existing data

        # Iterate through the table and insert supplier information into the database
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text()
            vat_number = self.table.item(row, 1).text()
            credit_account = self.table.item(row, 2).text()

            cursor.execute("INSERT INTO suppliers (name, vat_number, credit_account) VALUES (?, ?, ?)",
                           (name, vat_number, credit_account))

        self.conn.commit()
        self.show_message_box("Changes saved successfully.")

    def set_table_item(self, row, column, value):
        item = QTableWidgetItem(value)
        self.table.setItem(row, column, item)

    def clear_table_row(self, row):
        for col in range(self.table.columnCount()):
            self.set_table_item(row, col, "")

    def show_message_box(self, message):
        QMessageBox.information(self, "Message", message)


if __name__ == "__main__":
    app = QApplication([])
    window = SupplierManagement()
    window.show()
    app.exec_()
