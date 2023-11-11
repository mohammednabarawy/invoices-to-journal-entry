import pandas as pd

# Project variables
imam1_build_material_account = '50213'
imam1_vat_account = '21052'
imam1_credit_account = '2101171'
imam1_cost_center = '201'

imam3_build_material_account = '1201220'
imam3_vat_account = '21054'
imam3_credit_account = '2101171'
imam3_cost_center = '107'

turky_build_material_account = '1201220'
turky_vat_account = '21054'
turky_credit_account = '2101171'
turky_cost_center = '102'

imam2_build_material_account = '50813'
imam2_vat_account = '21052'
imam2_credit_account = '2101171'
imam2_cost_center = '106'

# Read the input Excel file
df = pd.read_excel('C:\\Users\\aghna\\Desktop\\تحويل الفواتير الى قيد يومية\\input_invoices.xlsx')

# Create an empty list to store the rows
output_rows = []

# Process each row of the input DataFrame
for index, row in df.iterrows():
    project = row['المشروع']

    # Skip the row if project name is not recognized
    if project == 'الامام1':
        build_material_account = imam1_build_material_account
        vat_account = imam1_vat_account
        credit_account = imam1_credit_account
        cost_center = imam1_cost_center
    elif project == 'الامام3':
        build_material_account = imam3_build_material_account
        vat_account = imam3_vat_account
        credit_account = imam3_credit_account
        cost_center = imam3_cost_center
    elif project == 'تركي الجديد':
        build_material_account = turky_build_material_account
        vat_account = turky_vat_account
        credit_account = turky_credit_account
        cost_center = turky_cost_center
    elif project == 'الامام2':
        build_material_account = imam2_build_material_account
        vat_account = imam2_vat_account
        credit_account = imam2_credit_account
        cost_center = imam2_cost_center
    else:
        continue

    date = row['التاريخ']
    origin_amount = row['اصل المبلغ']
    tax = row['الضريبة']
    total_amount = row['المبلغ شامل الضريبة']
    invoice_number = row['رقم الفاتورة']
    supplier = row['المورد']
    tax_number = row['الرقم الضريبي']

    
    # Add the debit entry for the origin amount
    output_rows.append(pd.Series({
        'التاريخ': date,
        'مدين': origin_amount,
        'دائن': '',
        'الحساب': f"مواد بناء {project}",
        'رقم الحساب': build_material_account,
        'مركز التكلفة': cost_center,
        'الوصف': f"مواد بناء {project} فاتورة {invoice_number}-{supplier}-{tax_number}"
    }))

    # Add the debit entry for the tax amount
    output_rows.append(pd.Series({
        'التاريخ': date,
        'مدين': tax,
        'دائن': '',
        'الحساب': 'ضريبة القيمة المضافة',
        'رقم الحساب': vat_account,
        'مركز التكلفة': cost_center,
        'الوصف': f"مواد بناء {project} فاتورة {invoice_number}-{supplier}-{tax_number}"
    }))

    # Add the credit entry for the total amount
    output_rows.append(pd.Series({
        'التاريخ': date,
        'مدين': '',
        'دائن': total_amount,
        'الحساب': supplier,
        'رقم الحساب': credit_account,
        'مركز التكلفة': cost_center,
        'الوصف': f"مواد بناء {project} فاتورة {invoice_number}-{supplier}-{tax_number}"
    }))

# Create the output DataFrame from the list of rows
output_df = pd.concat(output_rows, axis=1).T

# Write the output DataFrame to an Excel file
output_df.to_excel('C:\\Users\\aghna\\Desktop\\تحويل الفواتير الى قيد يومية\\output_file.xlsx', index=False)
print("Done!")