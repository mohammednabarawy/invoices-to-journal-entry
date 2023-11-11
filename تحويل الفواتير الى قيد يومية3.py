import pandas as pd

# Project accounts dictionary with default values
project_accounts = {
    'الامام1': {
        'build_material_account': '50213',
        'vat_account': '21052',
        'credit_account': '2101171',
        'cost_center': '201'
    },
    'الامام3': {
        'build_material_account': '1201220',
        'vat_account': '21054',
        'credit_account': '2101171',
        'cost_center': '107'
    },
    'تركي الجديد': {
        'build_material_account': '1201220',
        'vat_account': '21054',
        'credit_account': '2101171',
        'cost_center': '102'
    },
    'الامام2': {
        'build_material_account': '50813',
        'vat_account': '21052',
        'credit_account': '2101171',
        'cost_center': '106'
    }
}

# Read the input Excel file
input_file_path = 'C:\\Users\\aghna\\Desktop\\تحويل الفواتير الى قيد يومية\\input_invoices.xlsx'
df = pd.read_excel(input_file_path)

# Create an empty list to store the rows
output_rows = []

# Process each row of the input DataFrame
for index, row in df.iterrows():
    project = row['المشروع']

    # Create a new project if it doesn't exist
    if project not in project_accounts:
        print(
            f"Project '{project}' doesn't exist. Please provide the following details:")
        build_material_account = input("Debit Account for مواد بناء: ")
        vat_account = input("VAT Account for مواد بناء: ")
        credit_account = input("Credit Account for مواد بناء: ")
        cost_center = input("Cost Center for مواد بناء: ")

        project_accounts[project] = {
            'build_material_account': build_material_account,
            'vat_account': vat_account,
            'credit_account': credit_account,
            'cost_center': cost_center
        }

    # Retrieve project accounts
    project_info = project_accounts[project]
    build_material_account = project_info['build_material_account']
    vat_account = project_info['vat_account']
    credit_account = project_info['credit_account']
    cost_center = project_info['cost_center']

    # Extract required data from the input row
    date = row['التاريخ']
    origin_amount = row['اصل المبلغ']
    tax = row['الضريبة']
    total_amount = row['المبلغ شامل الضريبة']
    invoice_number = row['رقم الفاتورة']
    supplier = row['المورد']
    tax_number = row['الرقم الضريبي']

    # Create debit entry for the origin amount
    debit_entry = pd.Series({
        'التاريخ': date,
        'مدين': origin_amount,
        'دائن': '',
        'الحساب': f"مواد بناء {project}",
        'رقم الحساب': build_material_account,
        'مركز التكلفة': cost_center,
        'الوصف': f"مواد بناء {project} فاتورة {invoice_number}-{supplier}-{tax_number}"
    })
    output_rows.append(debit_entry)

    # Create debit entry for the tax amount
    debit_entry_tax = pd.Series({
        'التاريخ': date,
        'مدين': tax,
        'دائن': '',
        'الحساب': 'ضريبة القيمة المضافة',
        'رقم الحساب': vat_account,
        'مركز التكلفة': cost_center,
        'الوصف': f"مواد بناء {project} فاتورة {invoice_number}-{supplier}-{tax_number}"
    })
    output_rows.append(debit_entry_tax)

    # Create credit entry for the total amount
    credit_entry = pd.Series({
        'التاريخ': date,
        'مدين': '',
        'دائن': total_amount,
        'الحساب': supplier,
        'رقم الحساب': credit_account,
        'مركز التكلفة': cost_center,
        'الوصف': f"مواد بناء {project} فاتورة {invoice_number}-{supplier}-{tax_number}"
    })
    output_rows.append(credit_entry)

# Create the output DataFrame from the list of rows
output_df = pd.concat(output_rows, axis=1).T

# Write the output DataFrame to an Excel file
output_file_path = 'C:\\Users\\aghna\\Desktop\\تحويل الفواتير الى قيد يومية\\output_file.xlsx'
output_df.to_excel(output_file_path, index=False)

print("Conversion completed successfully. The output is saved in:", output_file_path)
