def compare_schemas(old_schema, new_schema):

    old_columns = set(old_schema.keys())
    new_columns = set(new_schema.keys())

    added_columns = new_columns - old_columns
    removed_columns = old_columns - new_columns

    common_columns = old_columns & new_columns

    changes = []

    for column in added_columns:

        changes.append({
            "column": column,
            "change_type": "COLUMN_ADDED",
            "severity": "LOW"
        })

    for column in removed_columns:

        changes.append({
            "column": column,
            "change_type": "COLUMN_REMOVED",
            "severity": "HIGH"
        })

    for column in common_columns:

        if old_schema[column]["datatype"] != new_schema[column]["datatype"]:

            changes.append({
                "column": column,
                "change_type": "DATATYPE_CHANGED",
                "old_value": old_schema[column]["datatype"],
                "new_value": new_schema[column]["datatype"],
                "severity": "HIGH"
            })

    for column in common_columns:

        if old_schema[column]["nullable"] != new_schema[column]["nullable"]:

            changes.append({
                "column": column,
                "change_type": "NULLABILITY_CHANGED",
                "old_value": old_schema[column]["nullable"],
                "new_value": new_schema[column]["nullable"],
                "severity": "HIGH"
            })

    return {
        "has_drift": len(changes) > 0,
        "changes": changes
    }

if __name__ == "__main__":

    old_schema = {
        "id": {
            "datatype": "integer",
            "nullable": False
        },
        "name": {
            "datatype": "varchar",
            "nullable": False
        },
        "age": {
            "datatype": "integer",
            "nullable": True
        },
        "email": {
            "datatype": "varchar",
            "nullable": True
        }
    }

    new_schema = {
        "id": {
            "datatype": "integer",
            "nullable": False
        },
        "name": {
            "datatype": "varchar",
            "nullable": False
        },
        "age": {
            "datatype": "varchar",
            "nullable": True
        },
        "email": {
            "datatype": "varchar",
            "nullable": False
        },
        "phone": {
            "datatype": "varchar",
            "nullable": True
        }
    }

    result = compare_schemas(old_schema, new_schema)

    print(result)