from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sqlite3


class Expense:
    def __init__(self, expense_id, project_name, expense_name, expense_account):
        self.expense_id = expense_id
        self.project_name = project_name
        self.expense_name = expense_name
        self.expense_account = expense_account


class ExpenseModel:
    def __init__(self, db_path='projects.db'):
        self.conn = sqlite3.connect(db_path)

    def get_expenses_by_project(self, project_name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM project_expenses WHERE project_name = ?", (project_name,))
            return [Expense(*row) for row in cursor.fetchall()]

    def update_expense(self, expense):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE project_expenses
                SET project_name = ?, expense_name = ?, expense_account = ?
                WHERE id = ?
            ''', (expense.project_name, expense.expense_name, expense.expense_account, expense.expense_id))

    def add_expense(self, expense):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO project_expenses (project_name, expense_name, expense_account)
                VALUES (?, ?, ?)
            ''', (expense.project_name, expense.expense_name, expense.expense_account))

    def delete_expense(self, expense_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                'DELETE FROM project_expenses WHERE id = ?', (expense_id,))


class ExpenseManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.expense_model = ExpenseModel()
        self.expense_table = QTableWidget(self)
        self.expenses = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Expense Management')
        self.setGeometry(300, 300, 800, 600)
        self.setStyleSheet("background-color: #f0f0f0; font-size: 14px;")

        self.project_selector = QComboBox(self)
        self.project_selector.currentIndexChanged.connect(
            self.display_expenses_table)

        self.expense_table.setColumnCount(4)
        self.expense_table.setHorizontalHeaderLabels(
            ['ID', 'Project Name', 'Expense Name', 'Expense Account'])
        self.expense_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.expense_table.itemSelectionChanged.connect(
            self.update_selected_expense)

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
        main_layout.addWidget(self.project_selector)
        main_layout.addWidget(self.expense_table)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.load_projects()
        self.display_expenses_table()
        self.adjust_table_columns()

    def load_projects(self):
        with self.expense_model.conn:
            cursor = self.expense_model.conn.cursor()
            cursor.execute(
                "SELECT DISTINCT project_name FROM project_expenses")
            projects = [row[0] for row in cursor.fetchall()]
            self.project_selector.addItems(projects)

    def display_expenses_table(self):
        selected_project = self.project_selector.currentText()
        self.expenses = self.expense_model.get_expenses_by_project(
            selected_project)

        self.expense_table.setRowCount(len(self.expenses))
        for row, expense in enumerate(self.expenses):
            self.populate_table_row(row, expense)

    def populate_table_row(self, row, expense):
        item_values = [expense.expense_id, expense.project_name,
                       expense.expense_name, expense.expense_account]
        for col, value in enumerate(item_values):
            item = QTableWidgetItem(str(value))
            self.expense_table.setItem(row, col, item)

    def update_selected_expense(self):
        selected_row = self.expense_table.currentRow()
        if 0 <= selected_row < len(self.expenses):
            self.current_expense_index = selected_row

    def save_changes_to_db(self):
        try:
            with self.expense_model.conn:
                cursor = self.expense_model.conn.cursor()
                for row in range(self.expense_table.rowCount()):
                    expense_id = int(self.expense_table.item(row, 0).text())
                    project_name = self.expense_table.item(row, 1).text()
                    expense_name = self.expense_table.item(row, 2).text()
                    expense_account = self.expense_table.item(row, 3).text()

                    if expense_id == 0:
                        # Insert a new record
                        cursor.execute('''
                            INSERT INTO project_expenses (project_name, expense_name, expense_account)
                            VALUES (?, ?, ?)
                        ''', (project_name, expense_name, expense_account))
                    else:
                        # Update an existing record
                        cursor.execute('''
                            UPDATE project_expenses
                            SET project_name = ?, expense_name = ?, expense_account = ?
                            WHERE id = ?
                        ''', (project_name, expense_name, expense_account, expense_id))
        except sqlite3.Error as e:
            self.show_message_box(f"Error saving changes: {e}")
        else:
            self.expense_model.conn.commit()
            self.expenses = self.expense_model.get_expenses_from_db()
            self.display_expenses_table()
            self.show_message_box("Changes saved successfully.")

    def add_row(self):
        current_project = self.project_selector.currentText()

        # Add a new row
        row_position = self.expense_table.rowCount()
        self.expense_table.insertRow(row_position)

        # Auto-fill ID with an auto-incremented number
        new_expense_id = self.get_next_expense_id(current_project)
        self.expense_table.setItem(
            row_position, 0, QTableWidgetItem(str(new_expense_id)))

    def get_next_expense_id(self, project_name):
        with self.expense_model.conn:
            cursor = self.expense_model.conn.cursor()
            cursor.execute(
                "SELECT COALESCE(MAX(id), 0) + 1 FROM project_expenses WHERE project_name = ?", (project_name,))
            return cursor.fetchone()[0]

    def delete_row(self):
        selected_row = self.expense_table.currentRow()
        if 0 <= selected_row < len(self.expenses):
            expense_id = int(self.expense_table.item(selected_row, 0).text())
            self.expense_model.delete_expense(expense_id)

            self.expenses = self.expense_model.get_expenses_by_project(
                self.project_selector.currentText())
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

    def adjust_table_columns(self):
        for col in range(self.expense_table.columnCount()):
            self.expense_table.resizeColumnToContents(col)

        table_width = self.expense_table.horizontalHeader().length() + 20
        self.setFixedWidth(max(table_width, 800))


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ExpenseManagement()
    window.show()
    sys.exit(app.exec_())
