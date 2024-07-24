from data_processing import credit_transactions_to_df, merge_mapping_with_transactions
from utils import load_environment, list_files
from chatgpt_interactions import send_multiple_chatGPT_queries
from utils import load_environment, load_reference, list_files


def main():
    data = load_reference()
    env_path = data["env_path"]
    load_environment(env_path)
    
    credit_statement_location = data["credit_statement_location"]
    files = list_files(credit_statement_location)

    df = credit_transactions_to_df(files, credit_statement_location)
    debit_transactions = df[df['Credit Amount'].isna()]['Transaction Description'].tolist()

    debit_categories = data["debit_categories"]
    
    credit_card_category_mappings = send_multiple_chatGPT_queries(data["first_prompt"], debit_transactions , debit_categories, data["follow_up_prompt"])

    final_df = merge_mapping_with_transactions(credit_card_category_mappings, df)

    final_df.to_csv(r"finances_categorised.csv",index=False)

if __name__ == "__main__":
    main()