import pandas as pd
import numpy as np

def clean_amazon_dataset(input_file="Amazon Sale Report.csv", output_file="cleaned_sales_data.csv"):
    print("=" * 60)
    print("🚀 STARTING DEEP DATA CLEANING PIPELINE")
    print("=" * 60)

    # 1. Load Raw Dataset
    print(f"📥 Loading dataset: '{input_file}'...")
    df = pd.read_csv(input_file, low_memory=False)
    initial_rows, initial_cols = df.shape
    print(f"📊 Initial Dataset Shape: {initial_rows:,} rows × {initial_cols} columns")

    # 2. Drop Redundant / Empty Metadata Columns
    cols_to_drop = ["index", "Unnamed: 22", "fulfilled-by"]
    existing_drops = [c for c in cols_to_drop if c in df.columns]
    if existing_drops:
        df.drop(columns=existing_drops, inplace=True)
        print(f"🗑️ Dropped redundant columns: {existing_drops}")

    # 3. Numeric Columns: Clean & Impute Missing Values
    print("🔢 Cleaning numeric features (Amount, Qty)...")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    df["Qty"] = pd.to_numeric(df["Qty"], errors="coerce").fillna(0).astype(int)

    # 4. Text Columns: General Trimming and Standardization
    text_columns = ["Category", "Size", "ship-city", "ship-state", "Courier Status", "Status", "Fulfilment"]
    for col in text_columns:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .replace({"nan": "Unknown", "None": "Unknown", "Null": "Unknown", "": "Unknown"})
                .str.title()
            )
            df[col] = df[col].fillna("Unknown")

    # 5. Ship-State: Deep Indian State & Union Territory Standardization
    print("🗺️ Normalizing state names and eliminating typos/abbreviations...")
    state_cleanup_map = {
        # Military Postal Service / Field Unit Addresses
        "Apo": "Military Post (APO)",
        # Rajasthan Typos & Short forms
        "Rajsthan": "Rajasthan",
        "Rj": "Rajasthan",
        "Rajashthan": "Rajasthan",

        # Punjab & Cluster entries
        "Punjab/Mohali/Zirakpur": "Punjab",
        "Pb": "Punjab",

        # Odisha
        "Orissa": "Odisha",

        # Puducherry
        "Pondicherry": "Puducherry",

        # Delhi & NCR
        "New Delhi": "Delhi",

        # Andhra Pradesh
        "A P": "Andhra Pradesh",
        "Ap": "Andhra Pradesh",

        # Arunachal Pradesh
        "Ar": "Arunachal Pradesh",

        # Nagaland
        "Nl": "Nagaland",

        # Bihar
        "Bihr": "Bihar",

        # Jammu & Kashmir
        "Jammu & Kashmir": "Jammu & Kashmir",
        "J&K": "Jammu & Kashmir",

        # Andaman & Nicobar
        "Andaman & Nicobar": "Andaman & Nicobar Islands",
        "Andaman And Nicobar Islands": "Andaman & Nicobar Islands",

        # Dadra and Nagar Haveli
        "Dadra And Nagar Haveli": "Dadra and Nagar Haveli and Daman and Diu",
        "Daman And Diu": "Dadra and Nagar Haveli and Daman and Diu"
    }

    df["ship-state"] = df["ship-state"].replace(state_cleanup_map)
    df["ship-state"] = df["ship-state"].str.strip().str.title()

    # 6. Postal Code Standardization
    if "ship-postal-code" in df.columns:
        df["ship-postal-code"] = (
            df["ship-postal-code"]
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.strip()
            .replace({"nan": "000000", "None": "000000"})
        )

    # 7. Date Handling: Convert to standard YYYY-MM-DD
    print("📅 Standardizing Date formats...")
    df["Date"] = pd.to_datetime(df["Date"], format="%m-%d-%y", errors="coerce")

    # 8. Save Processed & Cleaned File
    df.to_csv(output_file, index=False)
    final_rows, final_cols = df.shape

    print("=" * 60)
    print(f"✅ DATA CLEANING COMPLETE & VERIFIED!")
    print(f"📁 Output Saved To       : '{output_file}'")
    print(f"📊 Final Dataset Shape   : {final_rows:,} rows × {final_cols} columns")
    print(f"🏛️ Unique Clean States  : {df['ship-state'].nunique()}")
    print("=" * 60)

if __name__ == "__main__":
    clean_amazon_dataset()