import pandas as pd
from project_accounts import project_accounts


def create_project_accounts(project_name):
    if project_name in project_accounts:
        print(f"Project '{project_name}' already exists. Skipping.")
        return

    debit_account = project_accounts.get(project_name, {}).get('debit_account')
    if not debit_account:
        debit_account = input(
            f"Enter default debit account for project '{project_name}': ")

    vat_account = project_accounts.get(project_name, {}).get('vat_account')
    if not vat_account:
        vat_account = input(
            f"Enter VAT account for project '{project_name}': ")

    credit_account = project_accounts.get(
        project_name, {}).get('credit_account')
    if not credit_account:
        credit_account = input(
            f"Enter default credit account for project '{project_name}': ")

    cost_center = project_accounts.get(project_name, {}).get('cost_center')
    if not cost_center:
        cost_center = input(
            f"Enter cost center for project '{project_name}': ")

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
        invoice_number = str(row['Invoice Number'])
        date = row['Date']
        amount = row['Amount']
        tax = row['Tax']
        total_amount = row['Total Amount']
        project = row['Project']
        expense = row['Expense']
        vendor = row['Vendor']
        tax_number = row['Tax Number']

        if project not in project_accounts:
            create_project_accounts(project)

        if project not in project_accounts:
            print(f"Skipping invoice for project '{project}'.")
            continue

        debit_account = project_accounts[project]['debit_account']
        vat_account = project_accounts[project]['vat_account']
        credit_account = project_accounts[project]['credit_account']
        cost_center = project_accounts[project]['cost_center']

        # Create journal entries
        entry_debit = {
            'Date': date,
            'Debit': amount,
            'Credit': '',
            'Account': expense,
            'Account Number': debit_account,
            'Cost Center': cost_center,
            'Description': f"{expense} فاتورة {invoice_number}-{vendor}-{tax_number}"
        }
        output_rows.append(entry_debit)

        entry_tax = {
            'Date': date,
            'Debit': tax,
            'Credit': '',
            'Account': 'ضريبة القيمة المضافة',
            'Account Number': vat_account,
            'Cost Center': cost_center,
            'Description': f"فاتورة {invoice_number}-{vendor}-{tax_number}"
        }
        output_rows.append(entry_tax)

        entry_credit = {
            'Date': date,
            'Debit': '',
            'Credit': total_amount,
            'Account': vendor,
            'Account Number': credit_account,
            'Cost Center': cost_center,
            'Description': f"{vendor} فاتورة {invoice_number}-{vendor}-{tax_number}"
        }
        output_rows.append(entry_credit)

    output_df = pd.DataFrame(output_rows)
    output_df.to_excel(output_file, index=False)


# Usage example
input_file = '00.xlsx'
output_file = 'output_file.xlsx'
convert_invoices_to_journal(input_file, output_file)
