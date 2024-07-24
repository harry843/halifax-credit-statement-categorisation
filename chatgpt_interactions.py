import openai
import re
from utils import chunks
from json import load

# ChatGPT functions
def query_chatGPT(prompt: str) -> str:
    """ Takes string prompt to submit as a query to ChatGPT 3.5 Turbo
        Returns ChatGPT's response as a string
    """
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role":"user", "content":prompt}
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

def send_multiple_chatGPT_queries(first_prompt: str, debit_transactions: list , debit_categories: list, follow_up_prompt: str):
        # #### Fire off API requests

    # Loop through 100 transactions at a time, giving first prompt on first round and subsequently follow-up prompts only
    # boolean = True
    # for chunk in chunks(debit_transactions,n=100):
    #     if boolean:
    #         response = query_chatGPT(first_prompt.format(debit_categories, chunk))
            
    #         # Captures all text within curly brackets (aka the output dictionary)
    #         credit_card_category_mappings = extract_dict_from_chatGPT_response(response)
            
    #         boolean = False
            
    # #         print(first_prompt.format(debit_categories, chunk))
    #     else:
    #         pass
    #         response = query_chatGPT(follow_up_prompt.format(len(chunk), chunk))
            
    #         # Captures all text within curly brackets (aka the output dictionary)
    #         credit_card_category_mappings.update(extract_dict_from_chatGPT_response(response))

    # #         print(follow_up_prompt.format(len(chunk), chunk))

    with open('credit_card_category_mappings.json') as json_file:
        credit_card_category_mappings = load(json_file)

    return credit_card_category_mappings
