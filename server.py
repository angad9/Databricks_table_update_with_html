import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pyspark.sql import SparkSession

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Databricks_Update_Sheet").sheet1

# Read data
data = sheet.get_all_records()
spark = SparkSession.builder.getOrCreate()

for row in data:
    # Filter out empty values
    filtered_row = {k: v for k, v in row.items() if v != ""}
    if "id" not in filtered_row or len(filtered_row) == 1:
        continue  # Skip rows with no updates or only ID

    # Build dynamic SQL
    source_cols = ", ".join([f"'{v}' AS {k}" for k, v in filtered_row.items()])
    update_cols = ", ".join([f"t.{k} = s.{k}" for k in filtered_row.keys() if k != "id"])
    insert_cols = ", ".join(filtered_row.keys())
    insert_vals = ", ".join([f"s.{k}" for k in filtered_row.keys()])

    query = f"""
    MERGE INTO target_table t
    USING (SELECT {source_cols}) s
    ON t.id = s.id
    WHEN MATCHED THEN UPDATE SET {update_cols}
    WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
    """

    spark.sql(query)

print("Updates completed")