import argparse
import logging
import re

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")


def is_valid_email(email):
    if not email:
        return True
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


def is_valid_website(website):
    if not website:
        return True
    return re.match(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", website) is not None


def is_name_exists(df, name):
    return name in df["name"].values


def search_record(df):
    search_term = input("Enter the search term: ").strip().lower()
    search_results = df[df["name"].str.lower().str.contains(search_term)]
    if search_results.empty:
        logging.info("No records found.")
    else:
        logging.info("\n--- Search Results ---")
        for index, row in search_results.iterrows():
            logging.info(f"\nRecord {index + 1}:")
            for col, value in row.items():
                logging.info(f"{col}: {value if pd.notnull(value) else '[MISSING]'}")
    return df


def update_records(df):
    df["missing_count"] = df.isnull().sum(axis=1)
    max_missing_count = df["missing_count"].max()
    df_highest_missing = df[df["missing_count"] == max_missing_count].sample(frac=1)
    df_rest = df[df["missing_count"] != max_missing_count]
    df = pd.concat([df_highest_missing, df_rest]).drop(columns="missing_count")
    for index, row in df.iterrows():
        missing_fields = row[row.isnull()]

        if not missing_fields.empty:
            logging.info("\n--- Record Details ---")
            for col, value in row.items():
                logging.info(f"{col}: {value if pd.notnull(value) else '[MISSING]'}")

            logging.info("\nMissing Fields:")
            for col in missing_fields.index:
                logging.info(f"- {col}: [MISSING]")
                while True:
                    value = input(f"Please enter the value for '{col}': ").strip()
                    if col == "email" and not is_valid_email(value):
                        logging.info("Invalid email format. Please try again.")
                    elif col in ["website", "career_page", "linkedin"] and not is_valid_website(
                        value
                    ):
                        logging.info("Invalid website format. Please try again.")
                    else:
                        df.at[index, col] = value
                        break
            return df


def add_record(df):
    new_record = {}
    for col in df.columns:
        while True:
            value = input(f"Please enter the value for '{col}': ").strip()
            if col == "name" and is_name_exists(df, value):
                logging.info(f"Error: A record with the name '{value}' already exists.")
            elif col == "email" and not is_valid_email(value):
                logging.info("Invalid email format. Please try again.")
            elif col in ["website", "career_page", "linkedin"] and not is_valid_website(value):
                logging.info("Invalid website format. Please try again.")
            else:
                new_record[col] = value
                break
    df = df.append(new_record, ignore_index=True)
    return df


def process_csv_file(file_path, action):
    df = pd.read_csv(file_path)

    if action == "update":
        df = update_records(df)
    elif action == "add":
        df = add_record(df)
    elif action == "search":
        df = search_record(df)
        return

    df = df.sort_values(by="name")
    df.to_csv(file_path, index=False)
    logging.info(f"\nUpdated CSV file saved at {file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update, add, or search records in the CSV file.")
    parser.add_argument("--update", action="store_true", help="Update existing records.")
    parser.add_argument("--add", action="store_true", help="Add new records.")
    parser.add_argument("--search", action="store_true", help="Search for records.")
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        metavar="PATH",
        help="Path to the CSV file containing company data",
    )
    args = parser.parse_args()

    if args.update:
        process_csv_file(args.file, "update")
    elif args.add:
        process_csv_file(args.file, "add")
    elif args.search:
        process_csv_file(args.file, "search")
    else:
        logging.info("Please specify either --update, --add, or --search.")
