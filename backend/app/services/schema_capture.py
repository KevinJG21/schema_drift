import pandas as pd
from sqlalchemy import column


def get_datatype(series):

    if pd.api.types.is_integer_dtype(series):
        return "integer"

    if pd.api.types.is_float_dtype(series):
        return "float"

    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    return "string"


def capture_schema(file_path):

    df = pd.read_csv(file_path)

    columns = df.columns

    schema = {}

    for column in columns:

        datatype = get_datatype(df[column])


        nullable = bool(df[column].isnull().any())
        
        schema[column] = {
            "datatype": datatype,
            "nullable": nullable
        }

    return schema


if __name__ == "__main__":

    result = capture_schema("uploads/test_customers.csv")

    print(result)