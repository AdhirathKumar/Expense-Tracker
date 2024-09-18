import streamlit as st
import psycopg2
import pandas as pd  # Import pandas for DataFrame support
import datetime  # Import datetime module

# Establishing the connection
try:
    conn = psycopg2.connect(
        database="Expense Tracker",
        user="postgres",
        password="Ghutu2003$",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
except Exception as error:
    st.error(f"Error connecting to the database: {error}")


def month_number(month):
    months = {
        "January": "01", "February": "02", "March": "03",
        "April": "04", "May": "05", "June": "06",
        "July": "07", "August": "08", "September": "09",
        "October": "10", "November": "11", "December": "12"
    }
    return months.get(month, None)


def add_transaction(year, month, day, item_name, item_category, item_price, item_quantity, description):
    date_str = f"{year}-{month_number(month)}-{day:02d}"
    try:
        cursor.execute(
            """
            INSERT INTO transactions (transaction_date, item_name, item_category, item_price, item_quantity, description) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (date_str, item_name, item_category, item_price, item_quantity, description)
        )
        conn.commit()  # Commit the transaction
        st.success("Transaction added successfully!")
    except Exception as issue:
        st.error(f"Error adding transaction: {issue}")


def retrieve_transactions():
    try:
        cursor.execute("SELECT * FROM transactions ORDER BY transaction_date DESC")
        records = cursor.fetchall()

        if records:
            # Create a DataFrame from the records
            df = pd.DataFrame(records,
                              columns=["Transaction ID", "Transaction Date", "Item Name", "Item Category", "Item Price",
                                       "Item Quantity", "Total Amount", "Description"])
            df["Total Amount"] = df["Item Price"] * df[
                "Item Quantity"]  # Calculate total amount if not already calculated in DB

            # Reset index and create a new column for sequential IDs
            df.reset_index(drop=True, inplace=True)

            st.subheader("Transaction Records")
            st.dataframe(df)  # Display the DataFrame as a table
            return df  # Return DataFrame for further use
        else:
            st.write("No transactions found.")
            return None
    except Exception as issue:
        st.error(f"Error retrieving transactions: {issue}")
        return None


def delete_transaction(transaction_id):
    try:
        cursor.execute("DELETE FROM transactions WHERE transaction_id = %s", (transaction_id,))
        conn.commit()  # Commit the deletion
        st.success(f"Transaction ID {transaction_id} deleted successfully!")
    except Exception as issue:
        st.error(f"Error deleting transaction: {issue}")

def reset_data():
    try:
        cursor.execute("DROP TABLE transactions")
        cursor.execute("CREATE TABLE transactions (transaction_id SERIAL PRIMARY KEY,transaction_date DATE NOT NULL,item_name VARCHAR(255) NOT NULL,item_price DECIMAL(10, 2) NOT NULL,item_quantity INT NOT NULL,total_amount DECIMAL(10, 2) GENERATED ALWAYS AS (item_price * item_quantity) STORED NOT NULL,description VARCHAR(255));")
        conn.commit()
        st.success("Data reset successfully")
    except Exception as issue:
        st.error(f"Error resetting data: {issue}")

# Streamlit page configuration
st.set_page_config(page_title="Expense Tracker")
st.markdown("<h1 style='text-align: left; color: #4CAF50;'>Expense Tracker</h1>", unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Select a Page", ["Transaction Entry", "View Transactions"])

if page == "Transaction Entry":
    st.text("Date of transaction:")
    # Create three columns for year, month and day inputs
    col1, col2, col3 = st.columns(3)

    # Get current date
    today = datetime.date.today()

    with col1:
        input_year = st.selectbox(label="Select Year", options=[year for year in range(today.year, today.year + 5)],
                                  index=0)

    with col2:
        input_month = st.selectbox(label="Select Month", options=[
            "January", "February", "March", "April", "May",
            "June", "July", "August", "September",
            "October", "November", "December"
        ], index=today.month - 1)

    with col3:
        input_day = st.selectbox(label="Select Day", options=[day for day in range(1, 32)], index=today.day - 1)

    st.text("Transaction details:")
    # Create three columns for item name, price and quantity inputs
    col4, col5, col6, col7 = st.columns(4)

    with col4:
        input_item_name = st.text_input(label="Item Name",placeholder="Enter item name")


    with col5:
        input_item_category = st.selectbox(label="Item category",options=[
"Housing",
"Utilities",
"Transportation",
"Groceries",
"Dining Out",
"Insurance",
"Healthcare",
"Childcare",
"Pet Care",
"Personal Care",
"Clothing",
"Entertainment",
"Recreation",
"Travel",
"Savings and Investments",
"Emergency Fund",
"Debt Repayment",
"Education",
"Gifts and Donations",
"Miscellaneous Expenses",
"Home Improvement",
"Furnishings and Decor",
"Subscriptions",
"Legal Fees",
"Professional Fees",
"Child Activities",
"Charitable Donations",
"Emergency Fund Contributions",
"Retirement Savings",
"Investment Contributions",
"Taxes",
"Education Savings",
"Technology Expenses",
"Hobbies and Leisure Activities",
"Laundry and Dry Cleaning",
"Seasonal Expenses",
"Transportation Maintenance",
"Public Service Fees"
]
)  # Ensure quantity is at least 1
    with col6:
        input_item_price = st.number_input(label="Item Price", format="%0.2f")  # Format for decimal input

    with col7:
        input_item_quantity = st.number_input(label="Item Quantity", min_value=1)  # Ensure quantity is at least 1

    # Add a new input field for description
    input_description = st.text_input(label="Description",placeholder="Enter a description for transaction")

    if st.button(label="Add Transaction"):
        add_transaction(input_year, input_month, input_day, input_item_name, input_item_category,
                        input_item_price, input_item_quantity, input_description)

elif page == "View Transactions":
    st.header("View Transactions")

    df = retrieve_transactions()  # Retrieve transactions and store DataFrame

    if df is not None:  # If there are records available
        transaction_ids = df["Transaction ID"].tolist()  # Get list of transaction IDs

        selected_transaction_id = st.selectbox("Select Transaction ID to Delete:", options=transaction_ids)

        if st.button("Delete Transaction"):
            delete_transaction(selected_transaction_id)

        if st.button("Reset Data"):
            reset_data()

# Closing the cursor and connection when done
if cursor:
    cursor.close()
if conn:
    conn.close()