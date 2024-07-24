import pandas as pd
from datetime import datetime
import re

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
