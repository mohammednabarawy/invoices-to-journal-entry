import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtWidgets import QFileDialog  # Add QFileDialog import
import sqlite3
from settings_window import SettingsWindow
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QGridLayout, QFileDialog


class InvoiceProcessingApp(QWidget):
    def __init__(self):
        super().__init__()

        self.invoice_data = []
        self.init_ui()
        self.settings_window = SettingsWindow()

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

        self.settings_button = QPushButton('Settings')
        self.settings_button.clicked.connect(self.show_settings)

        # Create a grid layout for the buttons
        button_layout = QGridLayout()
        button_layout.addWidget(self.import_button, 0, 0)
        button_layout.addWidget(self.add_button, 0, 1)
        button_layout.addWidget(self.process_button, 0, 2)
        button_layout.addWidget(self.add_row_button, 1, 0)
        button_layout.addWidget(self.delete_row_button, 1, 1)
        button_layout.addWidget(self.settings_button, 1, 2)

        # Create table for invoice data
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            'Date', 'Origin Amount', 'Tax', 'Total Amount',
            'Project', 'Invoice Number', 'Supplier', 'Tax Number'
        ])

        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        # Initialize SQLite database and table
        self.conn = sqlite3.connect('projects.db')
        self.create_projects_table()

    def show_settings(self):
        self.settings_window.show()

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
        self.table.setRowCount(0)
        self.table.setColumnCount(df.shape[1])

        for row in range(df.shape[0]):
            self.table.insertRow(row)
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iloc[row, col]))
                self.table.setItem(row, col, item)

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
            # Fetch project details from the database
            project_details = self.get_project_details_from_db(project)
            if project_details:
                debit_account, vat_account, credit_account, cost_center = project_details
            else:
                error_rows.append(row)
                continue

            self.invoice_data.append({
                'Date': date,
                'Origin Amount': origin_amount,
                'Tax': tax,
                'Total Amount': total_amount,
                'Project': project,
                'Invoice Number': invoice_number,
                'Supplier': supplier,
                'Tax Number': tax_number,
                'Debit Account': debit_account,
                'VAT Account': vat_account,
                'Credit Account': credit_account,
                'Cost Center': cost_center
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

            # Implement the original script's logic here
            if project == 'الامام1':
                debit_account = '50213'
                vat_account = '21052'
                credit_account = '2101171'
                cost_center = '201'
            elif project == 'الامام3':
                debit_account = '1201220'
                vat_account = '21054'
                credit_account = '2101171'
                cost_center = '107'
            elif project == 'تركي الجديد':
                debit_account = '1201220'
                vat_account = '21054'
                credit_account = '2101171'
                cost_center = '102'
            elif project == 'الامام2':
                debit_account = '50813'
                vat_account = '21052'
                credit_account = '2101171'
                cost_center = '106'
            else:
                error_rows.append(row)
                if error_rows:
                    self.show_error_message(error_rows)
                return

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

    def show_message_box(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Process Complete")
        msg.exec_()

    def get_project_details_from_db(self, project_name):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT debit_account, vat_account, credit_account, cost_center FROM projects WHERE project_name = ?', (project_name,))
        return cursor.fetchone()

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
