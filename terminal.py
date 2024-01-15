import pandas as pd

# Read the input Excel file
df = pd.read_excel(
    'F:\\original\\coding\\invoices-to-journal-entry\\input_invoices.xlsx')

# Create an empty DataFrame to store the processed data
output_df = pd.DataFrame(columns=[
                         'التاريخ', 'مدين', 'دائن', 'الحساب', 'رقم الحساب', 'مركز التكلفة', 'الوصف'])

# Process each row of the input DataFrame
for index, row in df.iterrows():
    date = row['التاريخ']
    origin_amount = row['اصل المبلغ']
    tax = row['الضريبة']
    total_amount = row['المبلغ شامل الضريبة']
    project = row['المشروع']
    invoice_number = row['رقم الفاتورة']
    supplier = row['المورد']
    tax_number = row['الرقم الضريبي']

    # Determine account numbers and cost centers based on project name
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
    elif project == 'فلل التخصصي':
        debit_account = '1201915'
        vat_account = '21054'
        credit_account = '2101171'
        cost_center = '110'
    elif project == 'نخيل الجامعة':
        debit_account = '120162'
        vat_account = '21054'
        credit_account = '2101171'
        cost_center = '109'
    elif project == 'عمارة التخصصي':
        debit_account = '1202021'
        vat_account = '21054'
        credit_account = '2101171'
        cost_center = '111'
    else:
        # If project name is not recognized, skip this row
        continue

    # Add the debit entry for the origin amount
    output_df = pd.concat([output_df, pd.DataFrame({
        'التاريخ': [date],
        'مدين': [origin_amount],
        'دائن': [''],
        'الحساب': [f"مواد بناء {project}"],
        'رقم الحساب': [debit_account],
        'مركز التكلفة': [cost_center],
        'الوصف': [f"مواد بناء {project} فاتورة {invoice_number}-{supplier}-{tax_number}"]
    })])

    # Add the debit entry for the tax amount
    output_df = pd.concat([output_df, pd.DataFrame({
        'التاريخ': [date],
        'مدين': [tax],
        'دائن': [''],
        'الحساب': ['ضريبة القيمة المضافة'],
        'رقم الحساب': [vat_account],
        'مركز التكلفة': [cost_center],
        'الوصف': [f"مواد بناء {project} فاتورة {invoice_number}-{supplier}-{tax_number}"]
    })])

    # Add the credit entry for the total amount
    output_df = pd.concat([output_df, pd.DataFrame({
        'التاريخ': [date],
        'مدين': [''],
        'دائن': [total_amount],
        'الحساب': [supplier],
        'رقم الحساب': [credit_account],
        'مركز التكلفة': [cost_center],
        'الوصف': [f"مواد بناء {project} فاتورة {invoice_number}-{supplier}-{tax_number}"]
    })])

# Write the output DataFrame to an Excel file
output_df.to_excel(
    'F:\\original\\coding\\invoices-to-journal-entry\\output_file.xlsx', index=False)
print("Done!")
