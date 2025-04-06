#Building streamlit app

import streamlit as st
import pandas as pd
import pypyodbc
from groq import Groq
import re
from PIL import Image
import time

client=Groq(api_key='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')
st.set_page_config(layout="wide")

def connect_db():
    return pypyodbc.connect("Driver={ODBC Driver 17 for SQL Server};"
                            "Server=localhost;"
                            "Database=business_data;"
                            "Trusted_Connection=yes;")

#main pic
image2= Image.open('chatbot.png')
st.sidebar.image(image2, use_column_width=True)

st.sidebar.header('Filters')
#tablename input
table_name=st.sidebar.text_input('Table Name', 'car_info_web')
#schema input
schema_name=st.sidebar.text_input('Schema','[dbo]')

#banner image
image=Image.open('banner.png')
st.image(image, use_column_width=True, caption="Sales and AI Banner", output_format="PNG")

#setup 2 col
left_col, right_col = st.columns(2)

#to extract metadata from the table
def extract_table_metadata(table_name, schema_name):
    connection=connect_db()
    cursor=connection.cursor()
    metadata_query= f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'"
    cursor.execute(metadata_query)
    columns=cursor.fetchall()
    column_metadata={f"[{col[0]}]":col[1] for col in columns}
    connection.close()
    return column_metadata

#function to generate SQL query
def generate_sql_query(question, column_metadata, table_name, schema_name):
    full_table_name=f"{schema_name}.[{table_name}]"
    prompt=f"""Generate only 1 SQL query based on this question:{question}.
    The table to use is '{full_table_name}'. The columns are: {', '.join(column_metadata.keys())}.
    Use only the columns needed to answer the question, not all of them.
    Column [price] is money, so make sure you convert that to money before aggregating."""
    model_name='llama-3.1-8b-instant'
    chat_completion=client.chat.completions.create(
        messages=[
            {"role":"system", "content":"You are a helpful assistant."},
            {"role":"user", "content": prompt}
        ],
        model=model_name,
    )
    response=chat_completion.choices[0].message.content.strip()
    return extract_sql_from_response(response)

#extract only SQL query from the response
def extract_sql_from_response(response):
    queries=re.findall(r"SELECT.*?;", response, re.IGNORECASE | re.DOTALL)
    if queries:
        return queries[0].strip().rstrip(';')
    else:
        raise ValueError("No valid SQL query found.")

#fetching data from SQL
def fetch_answer_from_db(sql_query):
    connection=connect_db()
    cursor=connection.cursor()
    cursor.execute(sql_query)
    columns=[column[0] for column in cursor.description]
    result=cursor.fetchall()
    df=pd.DataFrame(result,columns=columns)
    connection.close()
    return df

#agent where answer the question based on the DataFrame
def answer_question_from_df(question,df):
    df_json=df.to_json(orient='records')
    prompt=f"Based on the following data, answer this question:{question}. Here is the data: {df_json}"
    model_name='llama-3.1-8b-instant'
    chat_completion=client.chat.completions.create(
        messages=[
            {"role":"system", "content":"You are a helpful assistant."},
            {"role":"user","content":prompt}
        ],
        model=model_name,
    )
    return chat_completion.choices[0].message.content.strip()

#retrying the function process if error occurs or the output is not legit
def run_with_retries(question, retries=3):
    success=False
    attempt=0
    result_df=None
    answer=None
    while attempt < retries and not success:
        try:
            attempt+=1
            column_metadata=extract_table_metadata(table_name, schema_name)
            sql_query=generate_sql_query(question, column_metadata, table_name, schema_name)
            #display the generated SQL query
            st.subheader(f"Generated SQL Query (Attempt {attempt})")
            st.code(sql_query)
            result_df=fetch_answer_from_db(sql_query)
            answer=answer_question_from_df(question, result_df)
            success=True #set as success if no error occurs
        except Exception as e:
            st.warning(f"Attempt {attempt} failed with error: {e}")
            time.sleep(1)
    if success:
        return result_df, answer
    else:
        st.error("Failed to process the request after three attempts.")
        return None, None

#question,input and answer set in left column
with left_col:
    st.header("Ask a Question")
    question=st.text_input("Enter your Question", "What are the costliest mobiles in our data with the price details?")
    if st.button('Submit'):
        df, answer = run_with_retries(question)
        if df is not None and answer is not None:
            st.subheader("Answer")
            st.write(answer)

#displaying the DataFrame on the right column
with right_col:
    st.header("Extracted Data")
    if 'df' in locals() and df is not None:
        st.dataframe(df)

#Streamlit run chatbot.py