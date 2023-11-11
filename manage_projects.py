from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QMessageBox, QHBoxLayout
import sqlite3


class ManageProjects(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.conn = sqlite3.connect('projects.db')
        self.projects = self.get_projects_from_db()
        self.current_project_index = 0
        self.display_current_project()

    def init_ui(self):
        self.setGeometry(300, 300, 400, 200)
        self.setWindowTitle('manage projects')

        # Input fields for project details
        self.project_name_input = QLineEdit()
        self.debit_account_input = QLineEdit()
        self.vat_account_input = QLineEdit()
        self.credit_account_input = QLineEdit()
        self.cost_center_input = QLineEdit()

        # Buttons for navigation and actions
        self.prev_button = QPushButton('Previous')
        self.next_button = QPushButton('Next')
        self.clear_button = QPushButton('Clear')
        self.add_button = QPushButton('Add')
        self.edit_button = QPushButton('Edit')
        self.delete_button = QPushButton('Delete')

        # Button connections
        self.prev_button.clicked.connect(self.show_previous_project)
        self.next_button.clicked.connect(self.show_next_project)
        self.clear_button.clicked.connect(self.clear_form)
        self.add_button.clicked.connect(self.add_project_to_db)
        self.edit_button.clicked.connect(self.edit_project)
        self.delete_button.clicked.connect(self.delete_project)

        # Labels for project number
        self.project_number_label = QLabel()

        # Layout for project details
        details_layout = QVBoxLayout()
        details_layout.addWidget(QLabel("Project Number:"))
        details_layout.addWidget(self.project_number_label)
        details_layout.addWidget(QLabel("Project Name:"))
        details_layout.addWidget(self.project_name_input)
        details_layout.addWidget(QLabel("Debit Account:"))
        details_layout.addWidget(self.debit_account_input)
        details_layout.addWidget(QLabel("VAT Account:"))
        details_layout.addWidget(self.vat_account_input)
        details_layout.addWidget(QLabel("Credit Account:"))
        details_layout.addWidget(self.credit_account_input)
        details_layout.addWidget(QLabel("Cost Center:"))
        details_layout.addWidget(self.cost_center_input)

        # Horizontal layout for navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)

        # Horizontal layout for action buttons
        action_layout = QHBoxLayout()
        action_layout.addWidget(self.clear_button)
        action_layout.addWidget(self.add_button)
        action_layout.addWidget(self.edit_button)
        action_layout.addWidget(self.delete_button)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(details_layout)
        main_layout.addLayout(nav_layout)
        main_layout.addLayout(action_layout)

        self.setLayout(main_layout)

    def get_projects_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects")
        return cursor.fetchall()

    def display_current_project(self):
        if self.projects:
            project = self.projects[self.current_project_index]
            self.project_number_label.setText(
                f"Project {self.current_project_index + 1} of {len(self.projects)}")
            self.project_name_input.setText(project[0])
            self.debit_account_input.setText(project[1])
            self.vat_account_input.setText(project[2])
            self.credit_account_input.setText(project[3])
            self.cost_center_input.setText(project[4])

    def show_previous_project(self):
        if self.current_project_index > 0:
            self.current_project_index -= 1
            self.display_current_project()

    def show_next_project(self):
        if self.current_project_index < len(self.projects) - 1:
            self.current_project_index += 1
            self.display_current_project()

    def clear_form(self):
        self.project_number_label.setText("")
        self.project_name_input.clear()
        self.debit_account_input.clear()
        self.vat_account_input.clear()
        self.credit_account_input.clear()
        self.cost_center_input.clear()

    def add_project_to_db(self):
        project_name = self.project_name_input.text()
        debit_account = self.debit_account_input.text()
        vat_account = self.vat_account_input.text()
        credit_account = self.credit_account_input.text()
        cost_center = self.cost_center_input.text()

        if project_name and debit_account and vat_account and credit_account and cost_center:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO projects (project_name, debit_account, vat_account, credit_account, cost_center)
                VALUES (?, ?, ?, ?, ?)
            ''', (project_name, debit_account, vat_account, credit_account, cost_center))
            self.conn.commit()

            # Update the displayed projects after adding
            self.projects = self.get_projects_from_db()
            self.current_project_index = len(self.projects) - 1
            self.display_current_project()
        else:
            self.show_message_box(
                "Please fill in all fields to add a project.")

    def edit_project(self):
        project_name = self.project_name_input.text()
        debit_account = self.debit_account_input.text()
        vat_account = self.vat_account_input.text()
        credit_account = self.credit_account_input.text()
        cost_center = self.cost_center_input.text()

        if project_name and debit_account and vat_account and credit_account and cost_center:
            if self.projects:
                cursor = self.conn.cursor()
                cursor.execute('''
                    UPDATE projects
                    SET debit_account = ?, vat_account = ?, credit_account = ?, cost_center = ?
                    WHERE project_name = ?
                ''', (debit_account, vat_account, credit_account, cost_center, project_name))
                self.conn.commit()

                self.show_message_box("Project details updated successfully.")
            else:
                self.show_message_box("No projects found in the database.")
        else:
            self.show_message_box(
                "Please fill in all fields to edit a project.")

    def delete_project(self):
        project_name = self.project_name_input.text()

        if project_name:
            cursor = self.conn.cursor()
            cursor.execute(
                'DELETE FROM projects WHERE project_name = ?', (project_name,))
            self.conn.commit()

            # Update the displayed projects after deletion
            self.projects = self.get_projects_from_db()
            if self.current_project_index >= len(self.projects):
                self.current_project_index = max(0, len(self.projects) - 1)
            self.display_current_project()
        else:
            self.show_message_box("Please specify a project name to delete.")

    def add_expense_to_db(self):
        # Logic to add the expense details to the project_expenses table
        pass

    def edit_expense(self):
        # Logic to edit the expense details in the project_expenses table
        pass

    def delete_expense(self):
        # Logic to delete the expense details from the project_expenses table
        pass

    def get_expenses_from_db(self):
        # Logic to retrieve expense details from the database
        pass

    def display_current_expense(self):
        # Logic to display the current expense details
        pass

    def show_message_box(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Message")
        msg.exec_()
