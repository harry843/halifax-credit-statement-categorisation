import pandas as pd
from datetime import datetime, timedelta
from PyPDF2 import PdfReader
from os import listdir, getenv
import re
import openai
from numpy import isnan
from dotenv import load_dotenv
from json import dump, load
from typing import Iterator


# ## Credit Card Statement Processing

# Load in environmental variables and define paths to local files
env_path = r"openai.env"
load_dotenv(dotenv_path=env_path)
openai.api_key = getenv("OPENAI_ACCESS_TOKEN")
credit_statement_location = input("Enter the path to the folder containing your pdf Halifax credit statements:")
files = [i for i in listdir(credit_statement_location) if i[-4:]==".pdf"]


# Utils Functions
def chunks(xs: list, n: int) -> Iterator[list]:
    """ Splits input list into len(xs)/n lists of n elements
    """
    n = max(1,n)
    return (xs[i:i+n] for i in range(0, len(xs), n))


# Data Quality Checks
def df_length_equals_pdf_length(df: pd.DataFrame, extracted_text: str):
    """ Checks whether length of output dataframe equals the
        length of the transactions table in the Pdf.
    """
    pattern = r'(\n\d{2}\s(?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER))'

    matches = re.findall(pattern,extracted_text)
    assert len(df) == len(matches), f"df of length {len(df)} does not equal matches of length {len(matches)}"
    
def impute_transaction_date(file_date: str, record: str):
    file_month, file_year = file_date.split('-')
    transaction_day, transaction_month = record.split(' ')[0:2]
    if file_month == 'Jan' and transaction_month == 'DECEMBER':
        return transaction_day + ' ' + transaction_month + ' ' + str(int(file_year) - 1)
    return transaction_day + ' ' + transaction_month + ' ' + file_year
        
    
def is_same_or_previous_month(parsed_date, file_date_string):
    # Parse the date strings into datetime objects
    file_date_obj = datetime.strptime(file_date_string, '%b-%y')

    # Check if the date is the same or one month before the file_date
    if parsed_date.month == file_date_obj.month and parsed_date.year == file_date_obj.year:
        return True
    elif parsed_date.month == (file_date_obj.month - 1) and parsed_date.year == file_date_obj.year:
        return True
    elif file_date_obj.month == 1:
        parsed_date.month == file_date_obj.month or parsed_date.month == 12
        return True
    else:
        return False
    
def is_valid_transaction_date(date: str, file_date: str):
    parsed_date = pd.to_datetime(date, format="%d %B %y")
    month, year = file_date.split('-')
    
    assert parsed_date <= datetime.now(), f"{file_date}: date extracted is in the future: {date}"

    # Check year is valid
    if month == 'Jan' and parsed_date.month == 12:
        assert str(parsed_date.year)[-2:] == str(int(year) - 1), f"File year {year} does not match year parsed {parsed_date.year}"
    else:
        assert str(parsed_date.year)[-2:] == year, f"File year {year} does not match year parsed {parsed_date.year}"
    
    # Check month is valid
    assert is_same_or_previous_month(parsed_date, file_date), f"File month {month} does not match month parsed {date.split(' ')[1]}"


# Function to turn Halifax Credit Card statementscredit
def credit_transactions_to_df(files: list) -> pd.DataFrame:
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

        reader = PdfReader(credit_statement_location + "\\" + f) 

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


# ChatGPT functions
def query_chatGPT(prompt: str) -> str:
    """ Takes string prompt to submit as a query to ChatGPT 3.5 Turbo
        Returns ChatGPT's response as a string
    """
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role":"user", "content":first_prompt.format(debit_categories, chunk)}
    ])
    response = completion.choices[0].message.content
    
    return response 

def extract_dict_from_chatGPT_response(response: str) -> dict:
    """ Searches ChatGPT's string response for text within curly brackets
        Returns all key:value pairs found as a dictionary
    """
    # Captures all text within curly brackets (aka the output dictionary)
    pattern = r'{(.*?)}'

    # Captures only the key and value, within single quotation marks in the string
    str_pattern = r"'([^']+)':\s+'([^']+)'"

    # Find all matches in the text
    matches = re.findall(pattern, response, re.DOTALL)

    # Extracted data inside and including the curly brackets
    dictionary={}

    for match in matches:
        # Find all matches in the string
        str_matches = re.findall(str_pattern, match)

        # Iterate through the matches and store them in the dictionary
        for str_match in str_matches:
            key = str_match[0]
            value = str_match[1]
            dictionary[key] = value
    
    return dictionary


# ### Convert PDF to DataFrame and define Categories

df = credit_transactions_to_df(files)

debit_transactions = df[df['Credit Amount'].isna()]['Transaction Description'].tolist()

debit_categories = ["Savings","Rent","Eating out","Transport","Groceries","Shopping","Holidays","Entertainment","Personal Care","General","Charity"]


# ### Notes on ChatGPT API

# * We are going to ask ChatGPT to categorise this transactional data for us
# * I have noticed that quality of ChatGPT's category assignment decreases with the length of the prompt
# * To combat this, I recommend splitting the debit_transactions data into manageable chunks
# * I will fire off multiple prompts to ChatGPT via the API, and concatenate the outputs using pandas
# * ChatGPT's categorisation is good, but not perfect - I advise manual spot checks to confirm you are happy with the results!

# #### Define ChatGPRT Prompts

first_prompt = """
I have the following list of transaction descriptions, which I want you to map to a category from the list of categories provided.   
Here is the list of categories: {}
Here is the list of transaction descriptions: {}
I don't want you to provide me the code for doing this. I want you to actually do the mapping, using the data provided.
Please give me your response as a dictionary object, in the form: "Transaction Description":"Category"
"""

follow_up_prompt = """
That's perfect! Can you repeat this task for the next {} transaction descriptions, returning an output with no duplicates?
Here are the transaction descriptions: {} 
"""


# #### Fire off API requests

# Loop through 100 transactions at a time, giving first prompt on first round and subsequently follow-up prompts only
boolean = True
for chunk in chunks(debit_transactions,n=100):
    if boolean:
#         response = query_chatGPT(first_prompt.format(debit_categories, chunk))
        
#         # Captures all text within curly brackets (aka the output dictionary)
#         credit_card_category_mappings = extract_dict_from_chatGPT_response(response)
        
        boolean = False
        
#         print(first_prompt.format(debit_categories, chunk))
    else:
        pass
#         response = query_chatGPT(follow_up_prompt.format(len(chunk), chunk))
        
#         # Captures all text within curly brackets (aka the output dictionary)
#         credit_card_category_mappings.update(extract_dict_from_chatGPT_response(response))

#         print(follow_up_prompt.format(len(chunk), chunk))


with open('credit_card_category_mappings.json') as json_file:
    credit_card_category_mappings = load(json_file)


# ### Merge category mappings with transactions dataframe

# Ensure transaction descriptions (keys) are uppercase for dataframe merge
transaction_categories = {k.upper():v for k,v in credit_card_category_mappings.items()}

# Convert to dictionary to dataframe
categories_df = pd.DataFrame(data=transaction_categories.items(),columns=["Transaction Description","Category"],index=range(len(transaction_categories)))

# Merge category mappings with all transaction records
credit_card_df = pd.merge(df, categories_df, on='Transaction Description', how='left')

# Find out what % of money spent using Credit Card has been categorised, against credit card repayments on debit card 
credit_card_df.groupby(['Category'])['Debit Amount'].sum().reset_index()

print(f"Total Spend on Credit Card Statements Processed: £{credit_card_df['Debit Amount'].sum()}")


# #### Recategorise Null Categories from Credit Card Statements via Chat GPT

uncategorised = credit_card_df[(credit_card_df['Category'].isna())&(credit_card_df['Transaction Description']!='DIRECT DEBIT PAYMENT - THANK YOU')]
if len(uncategorised) > 0:
    print(uncategorised['Transaction Description'].tolist())


# #### Data Cleaning: Remove Direct Debit Credit Payments

final_df = credit_card_df[~credit_card_df['Transaction Description'].str.contains("DIRECT DEBIT PAYMENT - THANK YOU|PAYMENT RECEIVED - THANK YOU",regex=True)].reset_index(drop=True)

final_df.to_csv(r"finances_categorised.csv",index=False)


