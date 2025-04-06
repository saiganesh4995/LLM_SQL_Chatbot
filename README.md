# LLM-Powered SQL Chatbot with Streamlit

This project is a Streamlit-based intelligent chatbot that allows users to ask natural language questions and receive insights from a SQL Server database. The chatbot uses the Groq LLM (LLaMA-3.1-8b-instant) to convert questions into SQL queries and provide user-friendly answers based on retrieved data.

## 🔧 Features

- 🌐 Natural language to SQL conversion via Groq LLM
- 🧠 Answers generated from retrieved DataFrames using LLM context
- 📊 Visual interface using Streamlit
- 🗂️ Supports querying the following tables:
  - `product_info`
  - `order_status`
  - `support_contacts`
  - `faq`
- 🔁 Retry mechanism for robustness

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- SQL Server with database `business_data` set up
- ODBC Driver 17 for SQL Server
- Groq API Key

### Installation

```bash
pip install streamlit pandas pypyodbc groq Pillow
```

### Run the App

```bash
streamlit run chatbot.py
```

## 📦 Database Schema & Sample Data

The app uses a SQL Server database `business_data` with the following tables:

### `product_info`

| Column      | Type          |
|-------------|---------------|
| product_id  | INT (PK)      |
| name        | VARCHAR(100)  |
| features    | TEXT          |
| price       | DECIMAL(10,2) |

### `order_status`

| Column        | Type          |
|---------------|---------------|
| order_id      | INT (PK)      |
| customer_name | VARCHAR(100)  |
| status        | VARCHAR(50)   |

### `support_contacts`

| Column     | Type         |
|------------|--------------|
| department | VARCHAR(100) (PK) |
| phone      | VARCHAR(50)  |
| email      | VARCHAR(100) |

### `faq`

| Column    | Type         |
|-----------|--------------|
| id        | INT (PK)     |
| question  | TEXT         |
| keywords  | VARCHAR(255) |
| answer    | TEXT         |

Sample data has been populated with 200 records in each table.

## 🧠 How It Works

1. The user inputs a natural language question.
2. Metadata about the table is extracted.
3. A prompt is sent to Groq to generate the SQL query.
4. The SQL query is executed on the selected table.
5. The results are sent back to Groq to form a human-readable answer.
6. The app displays both the answer and the resulting data.

## 📁 Files

- `chatbot.py`: Main application script
- `banner.png` and `chatbot.png`: UI images for branding
- `README.md`: This file

## 🛡️ Note

- Only the following tables are allowed for querying: `[dbo].[product_info], [dbo].[order_status], [dbo].[support_contacts], [dbo].[faq]`.
- Price aggregation handles `money` datatype conversion.


---

Made with ❤️ using Groq and Streamlit.