import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog, QComboBox, QHBoxLayout, QLabel
)
import sqlite3
from manage_projects import ManageProjects
from ExpenseManagement import ExpenseManagement


class InvoiceProcessingApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.manageprojects_window = ManageProjects()
        self.expense_management_window = ExpenseManagement()

    def init_ui(self):
        self.setWindowTitle('Invoice Processing App')
        self.setGeometry(100, 100, 800, 400)

        # Create buttons for various functionalities
        self.import_button = QPushButton('Import Invoices')
        self.import_button.clicked.connect(self.import_invoices)

        self.add_button = QPushButton('Add Invoice')
        self.add_button.clicked.connect(self.add_invoice)

        self.process_button = QPushButton('Process Invoices')
        self.process_button.clicked.connect(self.process_invoices)

        self.add_row_button = QPushButton('Add Row')
        self.add_row_button.clicked.connect(self.add_row)

        self.delete_row_button = QPushButton('Delete Row')
        self.delete_row_button.clicked.connect(self.delete_row)

        self.manageprojects_button = QPushButton('Manage Projects')
        self.manageprojects_button.clicked.connect(self.show_manageprojects)

        self.expense_management_button = QPushButton('Expense Management')
        self.expense_management_button.clicked.connect(
            self.show_expense_management)

        # Create a grid layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.process_button)
        button_layout.addWidget(self.add_row_button)
        button_layout.addWidget(self.delete_row_button)
        button_layout.addWidget(self.manageprojects_button)
        button_layout.addWidget(self.expense_management_button)

        # Create a label for instructions
        label = QLabel('Double-click on a cell to edit values.')

        # Create table for invoice data
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            'Date', 'Origin Amount', 'Tax', 'Total Amount',
            'Project', 'Invoice Number', 'Supplier', 'Tax Number', 'Expense',
            'Expense Account'
        ])

        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(label)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        # Initialize SQLite database and table
        self.conn = sqlite3.connect('projects.db')
        self.create_projects_table()

    def show_manageprojects(self):
        self.manageprojects_window.show()

    def show_expense_management(self):
        self.expense_management_window.show()

    def create_projects_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                project_name TEXT PRIMARY KEY,
                debit_account TEXT,
                vat_account TEXT,
                credit_account TEXT,
                cost_center TEXT
            )
        ''')
        self.conn.commit()

    def add_invoice(self):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        combo_box_projects = QComboBox()
        project_names = self.get_project_names_from_db()
        combo_box_projects.addItems(project_names)
        # Set for 'Project' column (index 4)
        self.table.setCellWidget(row_position, 4, combo_box_projects)

        combo_box_expenses = QComboBox()
        expense_names = self.get_expense_names_from_db()
        combo_box_expenses.addItems(expense_names)
        # Set for 'Expense' column (index 8)
        self.table.setCellWidget(row_position, 8, combo_box_expenses)

    def import_invoices(self):
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle('Select Excel File')
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Excel files (*.xlsx *.xls)")
        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()
            file_path = file_paths[0]  # Assuming a single file is selected

            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
                self.populate_table(df)

    def populate_table(self, df):
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1] + 2)

        for row in range(df.shape[0]):
            unmatched_project = False
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iloc[row, col]))
                self.table.setItem(row, col, item)

            combo_box_projects = QComboBox()
            project_names = self.get_project_names_from_db()
            combo_box_projects.addItems(project_names)
            self.table.setCellWidget(row, 4, combo_box_projects)

            imported_project_name = str(df.iloc[row, 4])
            matched_index = combo_box_projects.findText(imported_project_name)
            if matched_index >= 0:
                combo_box_projects.setCurrentIndex(matched_index)
            else:
                unmatched_project = True
                break

            combo_box_expenses = QComboBox()
            expense_names = self.get_expense_names_from_db()
            combo_box_expenses.addItems(expense_names)
            self.table.setCellWidget(row, df.shape[1], combo_box_expenses)

            if unmatched_project:
                self.table.removeRow(row)
                QMessageBox.warning(self, "Unmatched Project",
                                    f"Row {row + 1} contains an unmatched project: {imported_project_name}. This row will be skipped.")

    def get_expense_names_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT expense_name FROM project_expenses")
        return [name[0] for name in cursor.fetchall()]

    def get_project_details_from_db(self, project_name):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT debit_account, vat_account, credit_account, cost_center FROM projects WHERE project_name = ?', (project_name,))
        return cursor.fetchone()

    def process_invoices(self):
        self.invoice_data = []
        error_rows = []  # To store rows with unrecognized project names
        # Retrieve invoice data from the table
        for row in range(self.table.rowCount()):
            date = self.table.item(row, 0).text()
            origin_amount = float(self.table.item(row, 1).text())
            tax = float(self.table.item(row, 2).text())
            total_amount = float(self.table.item(row, 3).text())
            project = self.table.item(row, 4).text()
            invoice_number = self.table.item(row, 5).text()
            supplier = self.table.item(row, 6).text()
            tax_number = self.table.item(row, 7).text()
            expense = self.table.cellWidget(
                row, 8).currentText()  # Fetch the selected expense

            # Fetch project and expense details from the database
            project_details = self.get_project_details_from_db(project)
            expense_details = self.get_expense_details_from_db(expense)
            if project_details and expense_details:
                debit_account, vat_account, credit_account, cost_center = project_details
                expense_account = expense_details[0]
            else:
                error_rows.append(row)
                continue
            # Update the invoice data
            self.invoice_data.append({
                'Date': date,
                'Origin Amount': origin_amount,
                'Tax': tax,
                'Total Amount': total_amount,
                'Project': project,
                'Invoice Number': invoice_number,
                'Supplier': supplier,
                'Tax Number': tax_number,
                'Expense': expense,
                'Expense Account': expense_account
            })

        # Process each invoice and write to Excel
        for invoice in self.invoice_data:
            output_df = pd.DataFrame(columns=[
                'التاريخ', 'مدين', 'دائن', 'الحساب', 'رقم الحساب', 'مركز التكلفة', 'الوصف'])

            # Implement the original script's logic here using invoice data
            date = invoice['Date']
            origin_amount = invoice['Origin Amount']
            tax = invoice['Tax']
            total_amount = invoice['Total Amount']
            project = invoice['Project']
            invoice_number = invoice['Invoice Number']
            supplier = invoice['Supplier']
            tax_number = invoice['Tax Number']
            expense = invoice['Expense']
            expense_account = invoice['Expense Account']

            # Replace the hard-coded logic
            output_df = pd.concat([output_df, pd.DataFrame({
                'التاريخ': [date],
                'مدين': [origin_amount],
                'دائن': [''],
                'الحساب': [f"مواد بناء {project}"],
                'رقم الحساب': [debit_account],
                'مركز التكلفة': [cost_center],
                'الوصف': [f"مواد بناء {project} فاتورة {invoice_number}-{supplier}-{tax_number}"]
            })])

            output_df = pd.concat([output_df, pd.DataFrame({
                'التاريخ': [date],
                'مدين': [tax],
                'دائن': [''],
                'الحساب': ['ضريبة القيمة المضافة'],
                'رقم الحساب': [vat_account],
                'مركز التكلفة': [cost_center],
                'الوصف': [f"مواد بناء {project} فاتورة {invoice_number}-{supplier}-{tax_number}"]
            })])

            output_df = pd.concat([output_df, pd.DataFrame({
                'التاريخ': [date],
                'مدين': [''],
                'دائن': [total_amount],
                'الحساب': [supplier],
                'رقم الحساب': [credit_account],
                'مركز التكلفة': [cost_center],
                'الوصف': [f"مواد بناء {project} فاتورة {invoice_number}-{supplier}-{tax_number}"]
            })])

            # Append the processed invoice data to the output DataFrame
            if 'processed_df' not in locals():
                processed_df = output_df
            else:
                processed_df = pd.concat(
                    [processed_df, output_df], ignore_index=True)

        # Write the output DataFrame to an Excel file
        output_file = 'processed_invoices.xlsx'
        processed_df.to_excel(output_file, index=False)
        self.show_message_box(f"Processed invoices saved to: {output_file}")

        # Clear the table after processing
        self.table.clearContents()
        self.table.setRowCount(0)

        if error_rows:
            self.show_error_message(error_rows)

    def get_project_account_details_from_db(self, project_name):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT debit_account, vat_account, credit_account, cost_center
            FROM projects
            WHERE project_name = ?
        ''', (project_name,))
        return cursor.fetchone()

    def get_expense_details_from_db(self, expense_name):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT expense_account FROM project_expenses WHERE expense_name = ?", (expense_name,))
        return cursor.fetchone()

    def show_message_box(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Process Complete")
        msg.exec_()

    def get_project_names_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT project_name FROM projects")
        return [name[0] for name in cursor.fetchall()]

    def show_error_message(self, error_rows):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(
            "Project name not recognized. Please check the project name in the following rows:")
        msg.setInformativeText(
            f"Rows: {', '.join(str(row + 1) for row in error_rows)}")
        msg.setWindowTitle("Unrecognized Project Name")
        msg.exec_()

    def add_row(self):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        combo_box_projects = QComboBox()
        project_names = self.get_project_names_from_db()
        combo_box_projects.addItems(project_names)
        # Set for 'Project' column (index 4)
        self.table.setCellWidget(row_position, 4, combo_box_projects)

        combo_box_expenses = QComboBox()
        expense_names = self.get_expense_names_from_db()
        combo_box_expenses.addItems(expense_names)
        # Set for 'Expense' column (index 8)
        self.table.setCellWidget(row_position, 8, combo_box_expenses)

    def delete_row(self):
        selected_rows = set(index.row()
                            for index in self.table.selectedIndexes())
        if selected_rows:
            for row in sorted(selected_rows, reverse=True):
                self.table.removeRow(row)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InvoiceProcessingApp()
    window.show()
    sys.exit(app.exec_())
