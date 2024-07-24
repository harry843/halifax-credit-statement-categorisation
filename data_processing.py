import pandas as pd
from PyPDF2 import PdfReader
import re
from dq_checks import impute_transaction_date, is_valid_transaction_date, df_length_equals_pdf_length

# Function to turn Halifax Credit Card statementscredit
def credit_transactions_to_df(files: list, location: str) -> pd.DataFrame:
    """ Reads in a list of Halifax Pdf Bank Statements, extracts transaction
        data and transforms them into a pandas DataFrame.
    """
    df = pd.DataFrame()
    count = 1
    for f in files:
        file_date = f[-10:-4]
        year = f[-6:-4]
        
        if count == len(files):
            print(f"{file_date}\nCompleted")
        else:
            print(f"{file_date}",end=" -> ")

        reader = PdfReader(location + "\\" + f) 

        # getting a specific page from the pdf file (all my credit transactions are located on 1 page!)
        page = reader.pages[2] 

        # extracting text from page 
        text = page.extract_text() 

        # Apply the regex pattern to extract the desired text
        match = re.search(r'BALANCE FROM PREVIOUS STATEMENT([\s\S]*?)Customer Services:', text)

        extracted_text = match.group(1) if match else None
        assert extracted_text is not None, f"Failed to capture any data for {f[-10:-4]} statement"

        pattern = r'(\d{2}\s(?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER))'
        
        records = [t.strip() for t in extracted_text.split('\n') if re.findall(pattern,t)]

        credit_transactions = []
        for record in records:
            checking_df = pd.DataFrame()
            transaction_date = impute_transaction_date(file_date, record)
            # Check transaction date extracted is valid
            is_valid_transaction_date(transaction_date, file_date)
            description = ' '.join(record.split(' ')[4:-2]).strip().upper()
            if record.split(' ')[-1] == 'CR':
                credit_amount = record.split(' ')[-2].replace(",","")
                debit_amount = None
                credit_transactions.append({"Transaction Date": transaction_date, "Transaction Description":description, "Debit Amount":None, "Credit Amount":credit_amount})
            else:
                debit_amount = record.split(' ')[-1].replace(",","")
                credit_amount = None
                credit_transactions.append({"Transaction Date": transaction_date, "Transaction Description":description, "Debit Amount":debit_amount, "Credit Amount":None})
            part_df = pd.DataFrame(credit_transactions)
        # Check output df length equals number of records in pdf
        checking_df = pd.concat([checking_df,part_df])
        df_length_equals_pdf_length(part_df, extracted_text)
        df = pd.concat([df, part_df]).reset_index(drop=True)
        df_length_equals_pdf_length(part_df, extracted_text)
        # Increase count by 1 to track progress
        count += 1

    df['Transaction Date'] = pd.to_datetime(df['Transaction Date'], format="%d %B %y")
    df['Debit Amount'] = df['Debit Amount'].astype('float')
    df['Credit Amount'] = df['Credit Amount'].astype('float')
    df['Card Used'] = 'Halifax Credit'
    
    return df


def merge_mapping_with_transactions(credit_card_category_mappings: dict, df: pd.DataFrame):

    # Ensure transaction descriptions (keys) are uppercase for dataframe merge
    transaction_categories = {k.upper():v for k,v in credit_card_category_mappings.items()}

    # Convert to dictionary to dataframe
    categories_df = pd.DataFrame(data=transaction_categories.items(),columns=["Transaction Description","Category"],index=range(len(transaction_categories)))

    # Merge category mappings with all transaction records
    credit_card_df = pd.merge(df, categories_df, on='Transaction Description', how='left')

    # Find out what % of money spent using Credit Card has been categorised, against credit card repayments on debit card 
    credit_card_df.groupby(['Category'])['Debit Amount'].sum().reset_index()

    print(f"Total Spend on Credit Card Statements Processed: £{credit_card_df['Debit Amount'].sum()}")


    # #### Data Cleaning: Remove Direct Debit Credit Payments

    final_df = credit_card_df[~credit_card_df['Transaction Description'].str.contains("DIRECT DEBIT PAYMENT - THANK YOU|PAYMENT RECEIVED - THANK YOU",regex=True)].reset_index(drop=True)

    return final_df