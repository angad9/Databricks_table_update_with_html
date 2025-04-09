from fastapi import FastAPI
from pydantic import BaseModel
from databricks import sql
import os

app = FastAPI()

# Define the data model with optional fields
class UpdateData(BaseModel):
    id: str
    column1: str | None = None
    column2: str | None = None
    column3: str | None = None
    column4: str | None = None
    column5: str | None = None
    column6: str | None = None
    column7: str | None = None
    column8: str | None = None
    column9: str | None = None
    column10: str | None = None

# Databricks connection details
DATABRICKS_HOST = "your-databricks-host"
DATABRICKS_TOKEN = "your-databricks-token"
DATABRICKS_HTTP_PATH = "your-databricks-http-path"

@app.post("/update")
async def update_table(data: UpdateData):
    try:
        # Filter out None values to build dynamic update and insert clauses
        data_dict = {k: v for k, v in data.dict().items() if v is not None}
        if len(data_dict) == 1:  # Only 'id' provided
            return {"message": "No columns to update"}

        # Build the source row for MERGE
        source_cols = ", ".join([f"'{v}' AS {k}" for k, v in data_dict.items()])
        update_cols = ", ".join([f"t.{k} = s.{k}" for k in data_dict.keys() if k != "id"])
        insert_cols = ", ".join(data_dict.keys())
        insert_vals = ", ".join([f"s.{k}" for k in data_dict.keys()])

        # Construct the MERGE query
        query = f"""
        MERGE INTO target_table t
        USING (SELECT {source_cols}) s
        ON t.id = s.id
        WHEN MATCHED THEN UPDATE SET {update_cols}
        WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
        """

        # Connect to Databricks and execute
        connection = sql.connect(
            server_hostname=DATABRICKS_HOST,
            http_path=DATABRICKS_HTTP_PATH,
            access_token=DATABRICKS_TOKEN
        )
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()

        cursor.close()
        connection.close()

        return {"message": "Table updated successfully"}
    except Exception as e:
        return {"message": f"Error updating table: {str(e)}"}