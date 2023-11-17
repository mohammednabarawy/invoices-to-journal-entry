from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QMessageBox, QHBoxLayout, QFormLayout
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
        self.setWindowTitle('Manage Projects')

        # Input fields for project details
        self.project_name_input = QLineEdit()
        self.debit_account_input = QLineEdit()
        self.vat_account_input = QLineEdit()
        self.credit_account_input = QLineEdit()
        self.cost_center_input = QLineEdit()

        # Buttons for navigation and actions
        self.first_button = QPushButton('<<')
        self.prev_button = QPushButton('<')
        self.next_button = QPushButton('>')
        self.last_button = QPushButton('>>')
        self.clear_button = QPushButton('Clear')
        self.add_button = QPushButton('Add')
        self.edit_button = QPushButton('Edit')
        self.delete_button = QPushButton('Delete')

        # Button connections
        self.first_button.clicked.connect(self.go_to_first_project)
        self.prev_button.clicked.connect(self.show_previous_project)
        self.next_button.clicked.connect(self.show_next_project)
        self.last_button.clicked.connect(self.go_to_last_project)
        self.clear_button.clicked.connect(self.clear_form)
        self.add_button.clicked.connect(self.add_project_to_db)
        self.edit_button.clicked.connect(self.edit_project)
        self.delete_button.clicked.connect(self.delete_project)

        # Labels for project number
        self.project_number_label = QLabel()

        # Form layout for project details
        form_layout = QFormLayout()
        form_layout.addRow("Project Number:", self.project_number_label)
        form_layout.addRow("Project Name:", self.project_name_input)
        form_layout.addRow("Debit Account:", self.debit_account_input)
        form_layout.addRow("VAT Account:", self.vat_account_input)
        form_layout.addRow("Credit Account:", self.credit_account_input)
        form_layout.addRow("Cost Center:", self.cost_center_input)

        # Horizontal layout for navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.first_button)
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        nav_layout.addWidget(self.last_button)

        # Horizontal layout for action buttons
        action_layout = QHBoxLayout()
        action_layout.addWidget(self.clear_button)
        action_layout.addWidget(self.add_button)
        action_layout.addWidget(self.edit_button)
        action_layout.addWidget(self.delete_button)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(nav_layout)
        main_layout.addLayout(action_layout)

        self.setLayout(main_layout)

    def get_projects_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects")
        self.projects = cursor.fetchall()
        return self.projects

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

        if not self.validate_input(project_name, debit_account, vat_account, credit_account, cost_center):
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO projects (project_name, debit_account, vat_account, credit_account, cost_center)
                VALUES (?, ?, ?, ?, ?)
            ''', (project_name, debit_account, vat_account, credit_account, cost_center))
            self.conn.commit()

            # Update the displayed projects after adding
            self.get_projects_from_db()
            self.current_project_index = len(self.projects) - 1
            self.display_current_project()
            self.show_message_box("Project added successfully.")
        except Exception as e:
            self.show_message_box(f"Failed to add project: {e}")

    def edit_project(self):
        project_name = self.project_name_input.text()
        debit_account = self.debit_account_input.text()
        vat_account = self.vat_account_input.text()
        credit_account = self.credit_account_input.text()
        cost_center = self.cost_center_input.text()

        if not self.validate_input(project_name, debit_account, vat_account, credit_account, cost_center):
            return

        try:
            if self.projects:
                cursor = self.conn.cursor()
                cursor.execute('''
                    UPDATE projects
                    SET debit_account = ?, vat_account = ?, credit_account = ?, cost_center = ?
                    WHERE project_name = ?
                ''', (debit_account, vat_account, credit_account, cost_center, project_name))
                self.conn.commit()

                self.get_projects_from_db()
                self.show_message_box("Project details updated successfully.")
            else:
                self.show_message_box("No projects found in the database.")
        except Exception as e:
            self.show_message_box(f"Failed to update project details: {e}")

    def delete_project(self):
        project_name = self.project_name_input.text()

        if not project_name:
            self.show_message_box("Please specify a project name to delete.")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'DELETE FROM projects WHERE project_name = ?', (project_name,))
            self.conn.commit()

            # Update the displayed projects after deletion
            self.get_projects_from_db()
            if self.current_project_index >= len(self.projects):
                self.current_project_index = max(0, len(self.projects) - 1)
            self.display_current_project()
            self.show_message_box("Project deleted successfully.")
        except Exception as e:
            self.show_message_box(f"Failed to delete project: {e}")

    def validate_input(self, project_name, debit_account, vat_account, credit_account, cost_center):
        if not project_name or not debit_account or not vat_account or not credit_account or not cost_center:
            self.show_message_box("Please fill in all fields.")
            return False

        # Add additional validation checks if needed

        return True

    def show_message_box(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Message")
        msg.exec_()

    def go_to_first_project(self):
        if self.projects:
            self.current_project_index = 0
            self.display_current_project()

    def go_to_last_project(self):
        if self.projects:
            self.current_project_index = len(self.projects) - 1
            self.display_current_project()


# Example of usage
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ManageProjects()
    window.show()
    sys.exit(app.exec_())
