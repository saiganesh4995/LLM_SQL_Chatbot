# Building streamlit app

import streamlit as st
import pandas as pd
import mysql.connector
from groq import Groq
import re
from PIL import Image
import time

client = Groq(api_key='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')
st.set_page_config(layout="wide")

def connect_db():
    return mysql.connector.connect(
        host="sql12.freesqldatabase.com",
        user="sql12772444",
        password="qXLXi2hVqT",
        database="sql12772444",
        port=3306
    )

# main pic
image2 = Image.open('chatbot.png')
st.sidebar.image(image2, use_container_width=True)

st.sidebar.header('Filters')

# tablename input
if 'table_input' not in st.session_state:
    st.session_state.table_input = 'product_info'
table_name = st.sidebar.text_input('Table Name', value=st.session_state.table_input, key='table_input')

# banner image
image = Image.open('banner.png')
st.image(image, use_container_width=True,
         caption="Note: Please change the filter table name to the following option: product_info, order_status, support_contacts, faq",
         output_format="PNG")

# setup 2 col
left_col, right_col = st.columns(2)

# extract metadata from the table
def extract_table_metadata(table_name, schema_name=""):
    connection = connect_db()
    cursor = connection.cursor()
    metadata_query = f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'"
    cursor.execute(metadata_query)
    columns = cursor.fetchall()
    column_metadata = {f"`{col[0]}`": col[1] for col in columns}
    connection.close()
    return column_metadata

# generate SQL query
def generate_sql_query(question, column_metadata, table_name, schema_name=""):
    full_table_name = f"{table_name}"  # no schema used in MySQL
    allowed_tables = "product_info, order_status, support_contacts, faq"
    prompt = f"""
You are an expert SQL assistant. Generate ONLY ONE valid SQL query for the following question:

{question}

Use strictly the table: {full_table_name}. Do NOT use any other table.
The only allowed tables in this database are: {allowed_tables}.
The columns in this table are: {', '.join(column_metadata.keys())}.

Column [price] contains numeric values. Use it directly for sorting or aggregation.
"""
    model_name = 'llama-3.1-8b-instant'
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        model=model_name,
    )
    response = chat_completion.choices[0].message.content.strip()
    return extract_sql_from_response(response)

# extract only SQL query from the response
def extract_sql_from_response(response):
    queries = re.findall(r"SELECT.*?;", response, re.IGNORECASE | re.DOTALL)
    if queries:
        return queries[0].strip().rstrip(';')
    else:
        raise ValueError("No valid SQL query found.")

# fetch data from DB
def fetch_answer_from_db(sql_query):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute(sql_query)
    columns = [column[0] for column in cursor.description]
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=columns)
    connection.close()
    return df

# answer from DataFrame
def answer_question_from_df(question, df):
    df_json = df.to_json(orient='records')
    prompt = f"Based on the following data, answer this question: {question}. Here is the data: {df_json}"
    model_name = 'llama-3.1-8b-instant'
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        model=model_name,
    )
    return chat_completion.choices[0].message.content.strip()

# retry if error or invalid
def run_with_retries(question, retries=3):
    success = False
    attempt = 0
    result_df = None
    answer = None
    while attempt < retries and not success:
        try:
            attempt += 1
            column_metadata = extract_table_metadata(table_name)
            sql_query = generate_sql_query(question, column_metadata, table_name)
            st.subheader(f"Generated SQL Query (Attempt {attempt})")
            st.code(sql_query)
            result_df = fetch_answer_from_db(sql_query)
            answer = answer_question_from_df(question, result_df)
            success = True
        except Exception as e:
            st.warning(f"Attempt {attempt} failed with error: {e}")
            time.sleep(1)
    if success:
        return result_df, answer
    else:
        st.error("Failed to process the request after three attempts.")
        return None, None

# Question input (left column)
with left_col:
    st.header("Ask a Question")
    question = st.text_input("Enter your Question", "What are the costliest mobiles in our data with the price details?")
    if st.button('Submit'):
        df, answer = run_with_retries(question)
        if df is not None and answer is not None:
            st.subheader("Answer")
            st.write(answer)

# Data display (right column)
with right_col:
    st.header("Extracted Data")
    if 'df' in locals() and df is not None:
        st.dataframe(df)

# Run in terminal: streamlit run chatbot.py
