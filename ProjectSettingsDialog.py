import json
from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QFormLayout, QWidget


class ProjectSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Project Settings')

        # Load existing settings from JSON file
        self.project_settings = self.load_settings()

        self.project_widgets = []  # Store the project input widgets

        self.add_button = QPushButton('Add Project')
        self.add_button.clicked.connect(self.add_project)

        self.save_button = QPushButton('Save Settings')
        self.save_button.clicked.connect(self.save_settings)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.add_button)

        # If there are existing settings, display them in the dialog
        for project_name, project_settings in self.project_settings.items():
            project_widget = ProjectInputWidget()
            project_widget.set_values(project_name, project_settings)
            container = QWidget()
            container.setLayout(project_widget)
            self.project_widgets.append(container)
            self.layout.addWidget(container)

        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)

    def load_settings(self):
        try:
            with open('project_settings.json', 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            return {}

    def add_project(self):
        project_widget = ProjectInputWidget()
        container = QWidget()
        container.setLayout(project_widget)
        self.project_widgets.append(container)
        self.layout.insertWidget(len(self.project_widgets) + 1, container)

    def save_settings(self):
        all_project_settings = {}
        for container in self.project_widgets:
            widget = container.layout()
            project_name = widget.project_name_input.text()
            debit_account = widget.debit_input.text()
            vat_account = widget.vat_input.text()
            credit_account = widget.credit_input.text()
            cost_center = widget.cost_center_input.text()

            project_settings = {
                'debit_account': debit_account,
                'vat_account': vat_account,
                'credit_account': credit_account,
                'cost_center': cost_center
            }

            all_project_settings[project_name] = project_settings

        # Save settings to a JSON file
        with open('project_settings.json', 'w') as json_file:
            json.dump(all_project_settings, json_file, indent=4)

        print("Settings saved to project_settings.json")


class ProjectInputWidget(QFormLayout):
    def __init__(self):
        super().__init__()

        self.project_name_input = QLineEdit()
        self.debit_input = QLineEdit()
        self.vat_input = QLineEdit()
        self.credit_input = QLineEdit()
        self.cost_center_input = QLineEdit()

        self.addRow('Project Name:', self.project_name_input)
        self.addRow('Debit Account:', self.debit_input)
        self.addRow('VAT Account:', self.vat_input)
        self.addRow('Credit Account:', self.credit_input)
        self.addRow('Cost Center:', self.cost_center_input)

    def set_values(self, project_name, project_settings):
        self.project_name_input.setText(project_name)
        self.debit_input.setText(project_settings.get('debit_account', ''))
        self.vat_input.setText(project_settings.get('vat_account', ''))
        self.credit_input.setText(project_settings.get('credit_account', ''))
        self.cost_center_input.setText(project_settings.get('cost_center', ''))
