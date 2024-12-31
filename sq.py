import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect('customer_db.sqlite')

# Create a cursor object to execute SQL queries
cursor = connection.cursor()

# Fetch all records from the 'customer' table
cursor.execute("SELECT * FROM customer")

# Fetch all results from the query
customers = cursor.fetchall()

# Print the results
for customer in customers:
    print(customer)

# Close the connection
connection.close()
