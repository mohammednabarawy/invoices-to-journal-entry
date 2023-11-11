import pandas as pd
from project_accounts import project_accounts


def create_project_accounts(project_name):
    if project_name in project_accounts:
        print(f"Project '{project_name}' already exists. Skipping.")
        return

    debit_account = project_accounts.get(project_name, {}).get('debit_account')
    if not debit_account:
        debit_account = input("Enter default debit account for the project: ")

    vat_account = project_accounts.get(project_name, {}).get('vat_account')
    if not vat_account:
        vat_account = input("Enter VAT account for the project: ")

    credit_account = project_accounts.get(
        project_name, {}).get('credit_account')
    if not credit_account:
        credit_account = input(
            "Enter default credit account for the project: ")

    cost_center = project_accounts.get(project_name, {}).get('cost_center')
    if not cost_center:
        cost_center = input("Enter cost center for the project: ")

    project_accounts[project_name] = {
        'debit_account': debit_account,
        'vat_account': vat_account,
        'credit_account': credit_account,
        'cost_center': cost_center
    }


def convert_invoices_to_journal(input_file, output_file):
    try:
        df = pd.read_excel(input_file)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    except Exception as e:
        print(f"Error: Failed to read input file '{input_file}': {str(e)}")
        return

    output_rows = []

    for _, row in df.iterrows():
        project = row['Project']

        if project not in project_accounts:
            create_project_accounts(project)

        if project not in project_accounts:
            print(f"Skipping invoice for project '{project}'.")
            continue

        debit_account = project_accounts[project]['debit_account']
        vat_account = project_accounts[project]['vat_account']
        credit_account = project_accounts[project]['credit_account']
        cost_center = project_accounts[project]['cost_center']

        expense = row['Expense']
        date = row['Date']
        origin_amount = row['Origin Amount']
        tax = row['Tax']
        total_amount = row['Total Amount']
        invoice_number = row['Invoice Number']
        supplier = row['Supplier']
        tax_number = row['Tax Number']

        origin_entry = pd.Series({
            'Account': debit_account,
            'Account Number': '',
            'Description': f"Expense: {expense}, Invoice: {invoice_number}",
            'Debit': origin_amount,
            'Credit': 0,
            'Date': date,
            'Cost Center': cost_center
        })

        tax_entry = pd.Series({
            'Account': vat_account,
            'Account Number': '',
            'Description': f"VAT: {expense}, Invoice: {invoice_number}",
            'Debit': tax,
            'Credit': 0,
            'Date': date,
            'Cost Center': cost_center
        })

        total_entry = pd.Series({
            'Account': credit_account,
            'Account Number': '',
            'Description': f"Supplier: {supplier}, Invoice: {invoice_number}",
            'Debit': 0,
            'Credit': total_amount,
            'Date': date,
            'Cost Center': cost_center
        })

        output_rows.extend([origin_entry, tax_entry, total_entry])

    output_df = pd.DataFrame(output_rows)

    try:
        output_df.to_excel(output_file, index=False)
        print(f"Journal entries have been saved to '{output_file}'.")
    except Exception as e:
        print(
            f"Error: Failed to save journal entries to '{output_file}': {str(e)}")


# Usage example
convert_invoices_to_journal('input_invoices.xlsx', 'output_journal.xlsx')
