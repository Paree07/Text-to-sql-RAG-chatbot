import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Text-to-SQL Chatbot", layout="centered")

st.title("🤖 Text to SQL Chatbot")
st.info("💬 Ask questions like: total sales, highest sale, show all data")

st.markdown("""
### 💡 Examples:
- total sales
- show all data
- highest sale
- lowest sale
- average sales
- count of records

⚠️ Only database-related questions are supported.
""")

# session
if "messages" not in st.session_state:
    st.session_state.messages = []

# function: text → SQL
def text_to_sql(question):
    question = question.lower()

    if any(word in question for word in ["hello", "hi", "weather", "name", "how are you"]):
        return None

    if "total" in question or "sum" in question:
        return "SELECT SUM(amount) FROM sales"

    elif "average" in question:
        return "SELECT AVG(amount) FROM sales"

    elif "highest" in question:
        return "SELECT * FROM sales ORDER BY amount DESC LIMIT 1"

    elif "lowest" in question:
        return "SELECT * FROM sales ORDER BY amount ASC LIMIT 1"

    elif "count" in question:
        return "SELECT COUNT(*) FROM sales"

    elif "show" in question or "all" in question:
        return "SELECT * FROM sales"

    else:
        return None

# function: run SQL
def run_sql(query):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute(query)
    
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    conn.close()
    return columns, rows

# show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# input
prompt = st.chat_input("Ask something...")

if prompt:

    # show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.spinner("Thinking... 🤔"):

        sql = text_to_sql(prompt)

        if sql is None:
            response = "❌ Only database-related questions allowed"

            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.write(response)

        else:
            columns, result = run_sql(sql)

            if result:
                df = pd.DataFrame(result, columns=columns)
            else:
                df = pd.DataFrame()

            # smart response
            if "sum" in sql.lower():
                response = f"💰 Total sales is {result[0][0]}"
            elif "avg" in sql.lower():
                response = f"📊 Average sales is {result[0][0]}"
            elif "count" in sql.lower():
                response = f"🔢 Total records: {result[0][0]}"
            elif "desc" in sql.lower():
                response = "📈 Highest sale:"
            elif "asc" in sql.lower():
                response = "📉 Lowest sale:"
            else:
                response = "📋 Here is the data:"

            st.session_state.messages.append({"role": "assistant", "content": response})

            with st.chat_message("assistant"):
                st.write(response)
                st.dataframe(df)