import streamlit as st
import tempfile
import pandas as pd
from database.connection import DatabaseConnection
from database.metadata_reader import MetadataReader
from config.settings import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_DB_PORT,
    DEFAULT_SSH_PORT
)

# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🗄️" 
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title(APP_NAME)
st.caption(f"Version {APP_VERSION}")
st.divider()

# --------------------------------------------------
# CONNECTION NAME
# --------------------------------------------------

connection_name = st.text_input(
    "Connection Name",
    placeholder="Database Connection"
)

# --------------------------------------------------
# CONNECTION TYPE
# --------------------------------------------------

connection_type = st.radio(
    "Database Connection",
    [
        "Direct MySQL",
        "SSH Tunnel via PEM"
    ]
)
st.subheader("Connection Details")

# --------------------------------------------------
# DIRECT MYSQL
# --------------------------------------------------

if connection_type == "Direct MySQL":

    host = st.text_input("Host")

    port = st.number_input(
        "Port",
        value=DEFAULT_DB_PORT
    )

    database = st.text_input("Database")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

# --------------------------------------------------
# SSH TUNNEL
# --------------------------------------------------

else:

    ssh_host = st.text_input("SSH Host")

    ssh_port = st.number_input(
        "SSH Port",
        value=DEFAULT_SSH_PORT
    )

    ssh_user = st.text_input("SSH User")

    pem_file = st.file_uploader(
        "PEM File",
        type=["pem"]
    )

    st.divider()

    db_host = st.text_input("Database Host")

    db_port = st.number_input(
        "Database Port",
        value=DEFAULT_DB_PORT
    )

    db_name = st.text_input("Database Name")

    db_user = st.text_input("Database User")

    db_password = st.text_input(
        "Database Password",
        type="password"
    )

# --------------------------------------------------
# CONNECT BUTTON
# --------------------------------------------------

if st.button("Connect"):

    if not connection_name.strip():

        st.warning(
            "Please enter a Connection Name."
        )

        st.stop()

    try:

        db = DatabaseConnection()

        # ------------------------------------------
        # DIRECT MYSQL
        # ------------------------------------------

        if connection_type == "Direct MySQL":

            conn = db.connect_direct(
                host,
                port,
                database,
                username,
                password
            )

            st.session_state["db_host"] = host
            st.session_state["db_name"] = database
            st.session_state["db_user"] = username

        # ------------------------------------------
        # SSH TUNNEL
        # ------------------------------------------

        else:

            if pem_file is None:

                st.warning(
                    "Please upload a PEM file."
                )

                st.stop()

            temp_pem = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pem"
            )

            temp_pem.write(
                pem_file.getvalue()
            )

            temp_pem.close()

            conn = db.connect_ssh(
                ssh_host,
                ssh_port,
                ssh_user,
                temp_pem.name,
                db_host,
                db_port,
                db_name,
                db_user,
                db_password
            )

            st.session_state["db_host"] = db_host
            st.session_state["db_name"] = db_name
            st.session_state["db_user"] = db_user

        # ------------------------------------------
        # STORE SESSION
        # ------------------------------------------

        st.session_state["db"] = db

        st.session_state["db_connection"] = conn

        st.session_state["connection_name"] = (
            connection_name.strip()
        )

        st.session_state["connection_type"] = (
            connection_type
        )

    except Exception as e:

        st.error(str(e))

# --------------------------------------------------
# CONNECTION STATUS
# --------------------------------------------------

if "db_connection" in st.session_state:

    st.success(
        f"Database Connected Successfully : "
        f"{st.session_state['connection_name']}"
    )

    st.subheader("Database Information")

    st.write(
        f"Connection Name : "
        f"{st.session_state['connection_name']}"
    )

    st.write(
        f"Connection Type : "
        f"{st.session_state['connection_type']}"
    )

    st.write(
        f"DB User : "
        f"{st.session_state['db_user']}"
    )

    st.write(
        f"DB Name : "
        f"{st.session_state['db_name']}"
    )

    st.write(
        f"DB Host : "
        f"{st.session_state['db_host']}"
    )

    st.divider()

    reader = MetadataReader(
        st.session_state["db_connection"]
    )

    tables = reader.get_tables()

    # ------------------------------------------
    # TABLE NAMES
    # ------------------------------------------

    table_names = [
        table["table_name"]
        for table in tables
    ]

    st.subheader("Database Objects")

    st.write(
        f"Total Objects Found : {len(tables)}"
    )

    table_data = []

    for counter, table in enumerate(tables, start=1):

        table_data.append({
            "No.": counter,
            "Table Name": table["table_name"],
            "Type": table["table_type"],
            "Engine": table["engine"],
            "Rows": f"{table['rows']:,}",
            "Created": table["created"]
        })

    df = pd.DataFrame(table_data)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        # column_config={
        #     "No.": st.column_config.TextColumn(
        #         "No.",
        #         width="small"
        #     )
        # }
    )

    st.divider()

    st.subheader("Table Explorer")

    selected_table = st.selectbox(
        "Select a Table",
        table_names,
        index=None,
        placeholder="Choose a table..."
    )

    if not selected_table:
        st.info("Select a table to view its columns.")
    else:
        st.subheader(f"📋 Table : {selected_table}")
        columns = reader.get_columns(selected_table)
        column_data = []
        for column in columns:
            column_data.append({
                "Column": column["column_name"],
                "Type": column["column_type"],
                "Null": column["nullable"],
                "Key": column["key"],
                "Extra": column["extra"],
                "Default": column["default"]
            })
        df_columns = pd.DataFrame(column_data)
        st.dataframe(
            df_columns,
            use_container_width=True,
            hide_index=True
        )
        primary_keys = reader.get_primary_keys(selected_table)

        st.subheader("🔑 Primary Keys")
        if primary_keys:
            pk_data = []
            for pk in primary_keys:
                pk_data.append({
                    "Column": pk["column_name"]
                })
            st.dataframe(
                pd.DataFrame(pk_data),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No Primary Key")


        foreign_keys = reader.get_foreign_keys(selected_table)
        st.subheader("🔗 Foreign Keys")
        if foreign_keys:
            fk_data = []
            for fk in foreign_keys:
                fk_data.append({
                    "Column": fk["column_name"],
                    "References": f"{fk['referenced_table']}.{fk['referenced_column']}"
                })
            st.dataframe(
                pd.DataFrame(fk_data),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No Foreign Keys")


        indexes = reader.get_indexes(selected_table)

        st.subheader("📚 Indexes")
        if indexes:
            index_data = []
            for idx in indexes:
                index_data.append({
                    "Index": idx["index_name"],
                    "Column": idx["column_name"],
                    "Unique": "YES" if idx["non_unique"] == 0 else "NO"
                })
            st.dataframe(
                pd.DataFrame(index_data),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No Indexes")