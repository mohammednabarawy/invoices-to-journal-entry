from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QMessageBox, QHBoxLayout, QComboBox
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


class ExpenseManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('projects.db')
        self.expenses = self.get_expenses_from_db()
        self.current_expense_index = 0
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Expense Management')
        self.setGeometry(300, 300, 400, 200)

        self.project_combo_box = QComboBox()
        project_names = self.get_project_names_from_db()
        self.project_combo_box.addItems(project_names)

        project_name_label = QLabel("Project Name:")
        expense_name_label = QLabel("Expense Name:")
        expense_account_label = QLabel("Expense Account:")

        self.expense_name_input = QLineEdit()
        self.expense_account_input = QLineEdit()

        self.first_button = QPushButton('<<')
        self.prev_button = QPushButton('<')
        self.next_button = QPushButton('>')
        self.last_button = QPushButton('>>')
        self.clear_button = QPushButton('Clear')
        self.add_button = QPushButton('Add')
        self.edit_button = QPushButton('Edit')
        self.delete_button = QPushButton('Delete')

        self.first_button.clicked.connect(self.go_to_first_expense)
        self.prev_button.clicked.connect(self.show_previous_expense)
        self.next_button.clicked.connect(self.show_next_expense)
        self.last_button.clicked.connect(self.go_to_last_expense)
        self.clear_button.clicked.connect(self.clear_form)
        self.add_button.clicked.connect(self.add_expense_to_db)
        self.edit_button.clicked.connect(self.edit_expense)
        self.delete_button.clicked.connect(self.delete_expense)

        # Create a label for the current expense indicator
        self.current_expense_label = QLabel()

        details_layout = QVBoxLayout()
        # Add the label to the layout
        details_layout.addWidget(self.current_expense_label)
        details_layout.addWidget(QLabel("Select Project:"))
        details_layout.addWidget(self.project_combo_box)
        details_layout.addWidget(expense_name_label)
        details_layout.addWidget(self.expense_name_input)
        details_layout.addWidget(expense_account_label)
        details_layout.addWidget(self.expense_account_input)

        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.first_button)
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        nav_layout.addWidget(self.last_button)

        action_layout = QHBoxLayout()
        action_layout.addWidget(self.clear_button)
        action_layout.addWidget(self.add_button)
        action_layout.addWidget(self.edit_button)
        action_layout.addWidget(self.delete_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(details_layout)
        main_layout.addLayout(nav_layout)
        main_layout.addLayout(action_layout)

        self.setLayout(main_layout)
        self.update_expense_label()
        self.display_current_expense()

    def get_project_names_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT project_name FROM projects")
        # Fetch all project names and return as a list
        return [name[0] for name in cursor.fetchall()]

    def update_expense_label(self):
        total_expenses = len(self.expenses)
        if total_expenses > 0:
            self.current_expense_label.setText(
                f"Current Expense: {self.current_expense_index + 1} of {total_expenses}"
            )
        else:
            self.current_expense_label.setText("No expenses available.")

    def get_expenses_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM project_expenses")
        return cursor.fetchall()

    def display_current_expense(self):
        if self.expenses:
            current_expense = self.expenses[self.current_expense_index]
            # Assuming project_name is at index 1
            self.project_combo_box.setCurrentText(current_expense[1])
            # Assuming expense_name is at index 2
            self.expense_name_input.setText(current_expense[2])
            # Assuming expense_account is at index 3
            self.expense_account_input.setText(current_expense[3])

    def show_previous_expense(self):
        if self.current_expense_index > 0:
            self.current_expense_index -= 1
            self.display_current_expense()
            self.update_expense_label()

    def show_next_expense(self):
        if self.current_expense_index < len(self.expenses) - 1:
            self.current_expense_index += 1
            self.display_current_expense()
            self.update_expense_label()

    def clear_form(self):
        # Correct the line to clear the input fields
        self.expense_account_input.setText("")
        self.expense_name_input.setText("")
        # Reset the combo box to the first item
        self.project_combo_box.setCurrentIndex(0)

    def add_expense_to_db(self):
        project_name = self.project_combo_box.currentText()
        expense_name = self.expense_name_input.text()
        expense_account = self.expense_account_input.text()
        print(
            f"Adding: Project: {project_name}, Expense: {expense_name}, Account: {expense_account}")

        if project_name and expense_name and expense_account:
            cursor = self.conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO project_expenses (project_name, expense_name, expense_account)
                    VALUES (?, ?, ?)
                ''', (project_name, expense_name, expense_account))
                self.conn.commit()

                self.expenses = self.get_expenses_from_db()
                self.current_expense_index = len(self.expenses) - 1
                self.display_current_expense()
                self.update_expense_label()
            except Exception as e:
                print("Error adding expense to the database:", e)
                self.show_message_box(
                    "Failed to add expense. Please check the values and try again.")
        else:
            self.show_message_box(
                "Please fill in all fields to add an expense.")

    def edit_expense(self):
        project_name = self.project_combo_box.currentText()
        expense_name = self.expense_name_input.text()
        expense_account = self.expense_account_input.text()

        if project_name and expense_name and expense_account:
            if self.expenses:
                cursor = self.conn.cursor()
                cursor.execute('''
                    UPDATE project_expenses
                    SET expense_account = ?
                    WHERE project_name = ? AND expense_name = ?
                ''', (expense_account, project_name, expense_name))
                self.conn.commit()

                self.show_message_box("Expense details updated successfully.")
            else:
                self.show_message_box("No expenses found in the database.")
        else:
            self.show_message_box(
                "Please fill in all fields to edit an expense.")

    def delete_expense(self):
        project_name = self.project_combo_box.currentText()
        expense_name = self.expense_name_input.text()

        if project_name and expense_name:
            cursor = self.conn.cursor()
            cursor.execute(
                'DELETE FROM project_expenses WHERE project_name = ? AND expense_name = ?', (project_name, expense_name))
            self.conn.commit()

            self.show_message_box("Expense deleted successfully.")
            # Refresh the data from the database
            self.expenses = self.get_expenses_from_db()
            # If deleted the last expense, move to the previous one
            if self.current_expense_index >= len(self.expenses):
                self.current_expense_index = max(0, len(self.expenses) - 1)
            self.display_current_expense()
            self.update_expense_label()
        else:
            self.show_message_box(
                "Please specify the project name and expense name to delete.")

    def show_message_box(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Message")
        msg.exec_()

    def go_to_first_expense(self):
        if self.expenses:
            self.current_expense_index = 0
            self.display_current_expense()
            self.update_expense_label()

    def go_to_last_expense(self):
        if self.expenses:
            self.current_expense_index = len(self.expenses) - 1
            self.display_current_expense()
            self.update_expense_label()


# Example of usage
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ExpenseManagement()
    window.show()
    sys.exit(app.exec_())
