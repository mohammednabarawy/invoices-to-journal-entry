from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sqlite3


class ExpenseManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('projects.db')
        self.expense_table = QTableWidget(self)
        self.expenses = self.get_expenses_from_db()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Expense Management')
        self.setGeometry(300, 300, 800, 600)
        self.setStyleSheet("background-color: #f0f0f0; font-size: 14px;")

        self.expense_table.setColumnCount(4)
        self.expense_table.setHorizontalHeaderLabels(
            ['ID', 'Project Name', 'Expense Name', 'Expense Account'])
        self.expense_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.expense_table.itemSelectionChanged.connect(
            self.update_selected_expense)
        self.display_expenses_table()

        save_button = QPushButton('Save Changes')
        add_button = QPushButton('Add Row')
        delete_button = QPushButton('Delete Row')

        save_button.setStyleSheet("background-color: #2196f3; color: #ffffff;")
        add_button.setStyleSheet("background-color: #4caf50; color: #ffffff;")
        delete_button.setStyleSheet(
            "background-color: #f44336; color: #ffffff;")

        save_button.setIcon(QIcon('save_icon.png'))
        add_button.setIcon(QIcon('add_icon.png'))
        delete_button.setIcon(QIcon('delete_icon.png'))

        save_button.clicked.connect(self.save_changes_to_db)
        add_button.clicked.connect(self.add_row)
        delete_button.clicked.connect(self.delete_row)

        button_layout = QVBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(add_button)
        button_layout.addWidget(delete_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.expense_table)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        # Adjust column widths based on content
        for col in range(self.expense_table.columnCount()):
            self.expense_table.resizeColumnToContents(col)

        # Ensure the UI fits all columns
        table_width = self.expense_table.horizontalHeader().length() + \
            20  # Add a margin
        self.setFixedWidth(max(table_width, 800))  # Set minimum width to 800

    def display_expenses_table(self):
        self.expense_table.setRowCount(len(self.expenses))
        for row, expense in enumerate(self.expenses):
            for col, value in enumerate(expense):
                item = QTableWidgetItem(str(value))
                self.expense_table.setItem(row, col, item)

    def update_selected_expense(self):
        selected_row = self.expense_table.currentRow()
        if 0 <= selected_row < len(self.expenses):
            self.current_expense_index = selected_row

    def get_expenses_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM project_expenses")
        return cursor.fetchall()

    def save_changes_to_db(self):
        cursor = self.conn.cursor()
        for row in range(self.expense_table.rowCount()):
            expense_id = int(self.expense_table.item(row, 0).text())
            project_name = self.expense_table.item(row, 1).text()
            expense_name = self.expense_table.item(row, 2).text()
            expense_account = self.expense_table.item(row, 3).text()

            cursor.execute('''
                UPDATE project_expenses
                SET project_name = ?, expense_name = ?, expense_account = ?
                WHERE id = ?
            ''', (project_name, expense_name, expense_account, expense_id))

        self.conn.commit()
        self.expenses = self.get_expenses_from_db()
        self.display_expenses_table()
        self.show_message_box("Changes saved successfully.")

    def add_row(self):
        self.expense_table.setRowCount(self.expense_table.rowCount() + 1)

    def delete_row(self):
        selected_row = self.expense_table.currentRow()
        if 0 <= selected_row < len(self.expenses):
            expense_id = int(self.expense_table.item(selected_row, 0).text())
            cursor = self.conn.cursor()
            cursor.execute(
                'DELETE FROM project_expenses WHERE id = ?', (expense_id,))
            self.conn.commit()
            self.expenses = self.get_expenses_from_db()
            self.display_expenses_table()
            self.show_message_box("Row deleted successfully.")
        else:
            self.show_message_box("Please select a row to delete.")

    def show_message_box(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Message")
        msg.exec_()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ExpenseManagement()
    window.show()
    sys.exit(app.exec_())
