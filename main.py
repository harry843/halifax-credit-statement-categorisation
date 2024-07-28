from data_processing import credit_transactions_to_df, merge_mapping_with_transactions
from utils import load_environment, list_files
from chatgpt_interactions import send_multiple_chatGPT_queries
from utils import load_environment, load_reference, list_files


def main():
    data = load_reference()
    env_path = data["env_path"]
    load_environment(env_path)

    # Set variables from reference.json config
    debit_categories = data["debit_categories"]
    credit_statement_location = data["credit_statement_location"]
    files = list_files(credit_statement_location)

    # Convert unstructured pdf statements to structured data
    df = credit_transactions_to_df(files, credit_statement_location)
    debit_transactions = df[df['Credit Amount'].isna()]['Transaction Description'].tolist()

    # Query ChatGPT to map transaction descriptions to spend categories
    credit_card_category_mappings = send_multiple_chatGPT_queries(data["first_prompt"], debit_transactions , debit_categories, data["follow_up_prompt"])

    # Merge structured data with ChatGPT generated spend categories
    final_df = merge_mapping_with_transactions(credit_card_category_mappings, df)

    # Export final output to csv
    final_df.to_csv(r"finances_categorised.csv",index=False)

if __name__ == "__main__":
    main()
