import os

import pandas as pd
import requests
import streamlit as st


st.set_page_config(
    page_title="SchemaDrift",
    page_icon="🔍",
    layout="wide"
)


API_URL = os.getenv(
    "SCHEMA_DRIFT_API_URL",
    "http://localhost:8000"
).rstrip("/")


def get_datasets():
    response = requests.get(
        f"{API_URL}/datasets",
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def get_versions(dataset_name):
    response = requests.get(
        f"{API_URL}/datasets/{dataset_name}/versions",
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def get_drifts(dataset_name):
    response = requests.get(
        f"{API_URL}/datasets/{dataset_name}/drifts",
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def compare_versions(
    dataset_name,
    version_a,
    version_b
):
    response = requests.get(
        f"{API_URL}/datasets/{dataset_name}/compare",
        params={
            "version_a": version_a,
            "version_b": version_b
        },
        timeout=10
    )

    response.raise_for_status()

    return response.json()


st.title("🔍 SchemaDrift")

st.caption(
    "Schema Drift Intelligence Platform"
)


tab_analyze, tab_history, tab_compare = st.tabs(
    [
        "🔍 Analyze Dataset",
        "📚 Dataset History",
        "🔄 Compare Versions"
    ]
)


# ============================================================
# ANALYZE DATASET
# ============================================================

with tab_analyze:

    st.header("Analyze a CSV")

    st.write(
        "Upload a CSV dataset. The platform will capture "
        "its schema and compare it with the latest stored version."
    )

    dataset_name = st.text_input(
        "Dataset name",
        placeholder="e.g. olist_orders"
    )

    uploaded_file = st.file_uploader(
        "Upload CSV",
        type=["csv"]
    )

    if uploaded_file is not None:

        try:
            preview_df = pd.read_csv(
                uploaded_file,
                nrows=10
            )

            st.subheader("Preview")

            st.dataframe(
                preview_df,
                use_container_width=True
            )

            uploaded_file.seek(0)

            total_rows = sum(
                1
                for _ in uploaded_file
            ) - 1

            uploaded_file.seek(0)

            st.caption(
                f"{total_rows:,} rows • "
                f"{len(preview_df.columns)} columns"
            )

        except Exception as e:

            st.error(
                f"Unable to preview CSV: {e}"
            )

    if st.button(
        "🔎 Analyze Schema",
        use_container_width=True,
        type="primary"
    ):

        if not dataset_name.strip():

            st.error(
                "Please enter a dataset name."
            )

        elif uploaded_file is None:

            st.error(
                "Please upload a CSV file."
            )

        else:

            try:

                uploaded_file.seek(0)

                response = requests.post(
                    f"{API_URL}/datasets/"
                    f"{dataset_name.strip()}/check",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file,
                            "text/csv"
                        )
                    },
                    timeout=120
                )

                if response.status_code != 200:

                    try:
                        error_detail = response.json().get(
                            "detail",
                            "Analysis failed."
                        )
                    except Exception:
                        error_detail = (
                            "Analysis failed."
                        )

                    st.error(error_detail)

                else:

                    result = response.json()

                    st.success(
                        "Analysis completed."
                    )

                    st.divider()

                    st.subheader(
                        "Analysis Result"
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Dataset**")
                        st.write(
                            result["dataset"]
                        )

                    with col2:
                        st.write(
                            "**Schema Version**"
                        )
                        st.write(
                            result["version"]
                        )

                    drift = result["drift"]

                    st.divider()

                    if drift["has_drift"]:

                        st.warning(
                            "⚠️ **Schema Drift Detected**\n\n"
                            "Changes were detected compared "
                            "with the previous schema version."
                        )

                        st.subheader("Changes")

                        for change in drift["changes"]:

                            severity = change[
                                "severity"
                            ]

                            if severity == "HIGH":
                                icon = "🔴"
                            elif severity == "MEDIUM":
                                icon = "🟠"
                            else:
                                icon = "🟢"

                            col1, col2, col3 = st.columns(
                                [2, 2, 1]
                            )

                            with col1:
                                st.write(
                                    f"**{change['column']}**"
                                )

                            with col2:
                                st.write(
                                    change["change_type"]
                                )

                                if (
                                    change.get("old_value")
                                    is not None
                                    or
                                    change.get("new_value")
                                    is not None
                                ):

                                    old_value = change.get(
                                        "old_value"
                                    )

                                    new_value = change.get(
                                        "new_value"
                                    )

                                    st.caption(
                                        f"{old_value} → {new_value}"
                                    )

                            with col3:
                                st.write(
                                    f"{icon} {severity}"
                                )

                            st.divider()

                    else:

                        st.success(
                            "✅ No schema drift detected."
                        )

            except requests.RequestException as e:

                st.error(
                    f"Could not connect to backend: {e}"
                )

            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )


# ============================================================
# DATASET HISTORY
# ============================================================

with tab_history:

    st.header("Dataset History")

    try:

        datasets = get_datasets()

        if not datasets:

            st.info(
                "No datasets have been registered yet."
            )

        else:

            dataset_options = [
                dataset["name"]
                for dataset in datasets
            ]

            selected_dataset = st.selectbox(
                "Select Dataset",
                dataset_options,
                key="history_dataset"
            )

            st.divider()

            st.subheader(
                "Schema History"
            )

            versions = get_versions(
                selected_dataset
            )

            if versions:

                version_rows = []

                for version in versions:

                    schema = version[
                        "schema_json"
                    ]

                    version_rows.append(
                        {
                            "Version":
                                version[
                                    "version_number"
                                ],
                            "Columns":
                                len(schema),
                            "Created":
                                version.get(
                                    "created_at",
                                    ""
                                )
                        }
                    )

                st.dataframe(
                    pd.DataFrame(version_rows),
                    use_container_width=True,
                    hide_index=True
                )

                st.divider()

                st.subheader(
                    "Stored Schemas"
                )

                for version in versions:

                    with st.expander(
                        f"Version "
                        f"{version['version_number']}"
                    ):

                        schema = version[
                            "schema_json"
                        ]

                        schema_rows = []

                        for column, details in schema.items():

                            schema_rows.append(
                                {
                                    "Column": column,
                                    "Datatype":
                                        details.get(
                                            "datatype"
                                        ),
                                    "Nullable":
                                        details.get(
                                            "nullable"
                                        )
                                }
                            )

                        st.dataframe(
                            pd.DataFrame(
                                schema_rows
                            ),
                            use_container_width=True,
                            hide_index=True
                        )

            else:

                st.info(
                    "No schema versions found."
                )

            st.divider()

            st.subheader(
                "Drift History"
            )

            drifts = get_drifts(
                selected_dataset
            )

            if drifts:

                drift_rows = []

                for drift in drifts:

                    details = drift.get(
                        "details"
                    ) or {}

                    drift_rows.append(
                        {
                            "Version":
                                drift[
                                    "schema_version_id"
                                ],
                            "Column":
                                drift[
                                    "column_name"
                                ],
                            "Change":
                                drift[
                                    "change_type"
                                ],
                            "Severity":
                                drift[
                                    "severity"
                                ],
                            "Old":
                                details.get(
                                    "old_value"
                                ),
                            "New":
                                details.get(
                                    "new_value"
                                )
                        }
                    )

                st.dataframe(
                    pd.DataFrame(drift_rows),
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.success(
                    "No drift has been recorded."
                )

    except requests.RequestException as e:

        st.error(
            f"Could not connect to backend: {e}"
        )

    except Exception as e:

        st.error(
            f"Something went wrong: {e}"
        )


# ============================================================
# COMPARE VERSIONS
# ============================================================

with tab_compare:

    st.header("Compare Schema Versions")

    st.write(
        "Compare any two stored schema versions "
        "for the same dataset."
    )

    try:

        datasets = get_datasets()

        if not datasets:

            st.info(
                "No datasets have been registered yet."
            )

        else:

            dataset_options = [
                dataset["name"]
                for dataset in datasets
            ]

            selected_dataset = st.selectbox(
                "Dataset",
                dataset_options,
                key="compare_dataset"
            )

            versions = get_versions(
                selected_dataset
            )

            if len(versions) < 2:

                st.info(
                    "At least two schema versions "
                    "are required for comparison."
                )

            else:

                version_numbers = [
                    version["version_number"]
                    for version in versions
                ]

                col1, col2 = st.columns(2)

                with col1:

                    version_a = st.selectbox(
                        "Version A",
                        version_numbers,
                        index=0,
                        key="version_a"
                    )

                with col2:

                    default_index = (
                        len(version_numbers) - 1
                    )

                    version_b = st.selectbox(
                        "Version B",
                        version_numbers,
                        index=default_index,
                        key="version_b"
                    )

                st.caption(
                    f"Comparing Version {version_a} "
                    f"→ Version {version_b}"
                )

                if st.button(
                    "🔄 Compare Versions",
                    use_container_width=True,
                    type="primary"
                ):

                    if version_a == version_b:

                        st.warning(
                            "Please select two different versions."
                        )

                    else:

                        try:

                            result = compare_versions(
                                selected_dataset,
                                version_a,
                                version_b
                            )

                            comparison = result[
                                "comparison"
                            ]

                            st.divider()

                            st.subheader(
                                f"Version {version_a} "
                                f"vs Version {version_b}"
                            )

                            if not comparison[
                                "has_drift"
                            ]:

                                st.success(
                                    "✅ No schema differences "
                                    "were detected."
                                )

                            else:

                                changes = comparison[
                                    "changes"
                                ]

                                high_count = sum(
                                    1
                                    for change in changes
                                    if change["severity"]
                                    == "HIGH"
                                )

                                low_count = sum(
                                    1
                                    for change in changes
                                    if change["severity"]
                                    == "LOW"
                                )

                                col1, col2, col3 = st.columns(
                                    3
                                )

                                with col1:
                                    st.metric(
                                        "Total Changes",
                                        len(changes)
                                    )

                                with col2:
                                    st.metric(
                                        "High Severity",
                                        high_count
                                    )

                                with col3:
                                    st.metric(
                                        "Low Severity",
                                        low_count
                                    )

                                st.divider()

                                for change in changes:

                                    severity = change[
                                        "severity"
                                    ]

                                    if severity == "HIGH":
                                        icon = "🔴"
                                    elif severity == "MEDIUM":
                                        icon = "🟠"
                                    else:
                                        icon = "🟢"

                                    with st.container():

                                        col1, col2, col3 = st.columns(
                                            [2, 2, 1]
                                        )

                                        with col1:

                                            st.write(
                                                f"**{change['column']}**"
                                            )

                                        with col2:

                                            st.write(
                                                change[
                                                    "change_type"
                                                ]
                                            )

                                            old_value = change.get(
                                                "old_value"
                                            )

                                            new_value = change.get(
                                                "new_value"
                                            )

                                            if (
                                                old_value is not None
                                                or
                                                new_value is not None
                                            ):

                                                st.caption(
                                                    f"{old_value} "
                                                    f"→ "
                                                    f"{new_value}"
                                                )

                                        with col3:

                                            st.write(
                                                f"{icon} "
                                                f"{severity}"
                                            )

                                        st.divider()

                        except requests.RequestException as e:

                            st.error(
                                f"Comparison failed: {e}"
                            )

                        except Exception as e:

                            st.error(
                                f"Something went wrong: {e}"
                            )

    except requests.RequestException as e:

        st.error(
            f"Could not connect to backend: {e}"
        )

    except Exception as e:

        st.error(
            f"Something went wrong: {e}"
        )


st.divider()

st.caption(
    "Schema Drift Intelligence • "
    "Python • FastAPI • PostgreSQL • "
    "Apache Airflow • Docker"
)