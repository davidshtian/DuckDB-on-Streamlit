import streamlit as st
import duckdb
import platform

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Title of the Streamlit app
st.title("🦆 DuckDB on Streamlit")

# Sidebar for system and DuckDB information
st.sidebar.title("System Info")

# DuckDB version
duckdb_version = duckdb.__version__
st.sidebar.subheader("DuckDB Info")
st.sidebar.text(duckdb_version)

# Display OS information
st.sidebar.subheader("OS Info")
st.sidebar.text(platform.release())

# Function to get table names from a persistent DuckDB database
def get_table_names(conn):
    try:
        # Query to retrieve table names
        query = "SELECT table_schema as Schema, table_name as Table FROM information_schema.tables;"
        result = conn.query(query).df()
        return result
    except Exception as e:
        # Return the error message to be handled in the main code
        return str(e)

# Select Database Type selectbox
st.sidebar.subheader("Database Type")
db_type = st.sidebar.selectbox("Choose for", ["persistent", "memory"])

# Display tables if persistent is chosen
if db_type == "persistent":
    # Connect to DuckDB for retrieving table names
    conn = duckdb.connect(database='database.db', read_only=False)
    table_names_df = get_table_names(conn)
    if isinstance(table_names_df, str):  # Check if it's an error message
        st.session_state["messages"].append({"role": "assistant", "content": table_names_df})
    else:
        st.sidebar.subheader("Tables")
        st.sidebar.dataframe(table_names_df)
    conn.close()

# Add "Clear" button in the sidebar
st.sidebar.subheader("Clear")
if st.sidebar.button("Remove All History"):
    if "messages" in st.session_state:
        st.session_state["messages"] = []

# Placeholder for instructions
instructions_placeholder = st.empty()
if st.session_state["messages"] == []:
    instructions_placeholder.info("Please enter your SQL query.")

# Chat mode for SQL query input and output
query = st.chat_input("Enter your SQL query here")

if query:  # Check if the query is not empty
    # Append user's query to chat history
    st.session_state["messages"].append({"role": "user", "content": query})

    try:
        # Connect to DuckDB based on selected database type
        if db_type == "memory":
            # Use an in-memory database
            conn = duckdb.connect()
        else:
            # Use a persistent database file (change 'database.db' to your preferred file path)
            conn = duckdb.connect(database='database.db', read_only=False)

        # Execute the SQL query using DuckDB
        result = conn.query(query)

        if result is None or result.df().empty:
            st.session_state["messages"].append({"role": "assistant", "content": "Query executed successfully, but no data was returned."})
        else:
            # Display the result in a data frame format
            st.session_state["messages"].append({"role": "assistant", "content": result.df()})

    except Exception as e:
        # Append error message to chat history
        st.session_state["messages"].append({"role": "assistant", "content": f"Error executing query: {str(e)}"})
    finally:
        conn.close()

    # Clear the instructions message once the query is entered
    instructions_placeholder.empty()

# Display chat messages from history
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], str):
            st.markdown(message["content"])
        else:
            result_df = message["content"]
            st.dataframe(result_df)
