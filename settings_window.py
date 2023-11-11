from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QMessageBox
import sqlite3


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        # Establish connection to the database
        self.conn = sqlite3.connect('projects.db')

    def init_ui(self):
        self.setGeometry(300, 300, 400, 200)
        self.setWindowTitle('Settings')

        self.project_name_input = QLineEdit()
        self.debit_account_input = QLineEdit()
        self.vat_account_input = QLineEdit()
        self.credit_account_input = QLineEdit()
        self.cost_center_input = QLineEdit()

        self.add_project_button = QPushButton('Add Project')
        self.add_project_button.clicked.connect(self.add_project_to_db)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Project Name:"))
        layout.addWidget(self.project_name_input)
        layout.addWidget(QLabel("Debit Account:"))
        layout.addWidget(self.debit_account_input)
        layout.addWidget(QLabel("VAT Account:"))
        layout.addWidget(self.vat_account_input)
        layout.addWidget(QLabel("Credit Account:"))
        layout.addWidget(self.credit_account_input)
        layout.addWidget(QLabel("Cost Center:"))
        layout.addWidget(self.cost_center_input)
        layout.addWidget(self.add_project_button)

        self.setLayout(layout)

    def add_project_to_db(self):
        project_name = self.project_name_input.text()
        debit_account = self.debit_account_input.text()
        vat_account = self.vat_account_input.text()
        credit_account = self.credit_account_input.text()
        cost_center = self.cost_center_input.text()

        if project_name and debit_account and vat_account and credit_account and cost_center:
            cursor = self.conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO projects (project_name, debit_account, vat_account, credit_account, cost_center)
                    VALUES (?, ?, ?, ?, ?)
                ''', (project_name, debit_account, vat_account, credit_account, cost_center))
                self.conn.commit()
                self.show_success_message(
                    "Project added successfully to the database.")
            except sqlite3.IntegrityError:
                self.show_error_message(
                    "Project name already exists in the database.")
        else:
            self.show_error_message("Please fill in all fields.")

    def show_success_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Success")
        msg.exec_()

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec_()
