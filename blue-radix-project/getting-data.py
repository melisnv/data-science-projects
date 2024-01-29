import sqlite3
import csv

db_path = r'C:\Users\Melis Nur\Downloads\sqlite\sds.db'
connection = sqlite3.connect(db_path)

# creating a cursor
cursor = connection.cursor()

# getting table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# fetching data from each table and writing to CSV
for table in tables:
    table_name = table[0]
    query = f"SELECT * FROM {table_name};"

    # getting data
    cursor.execute(query)
    data = cursor.fetchall()

    # writing data to CSV file
    csv_filename = f"{table_name}.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)

        # header
        csv_writer.writerow([description[0] for description in cursor.description])

        # data rows
        csv_writer.writerows(data)

# closing cursor and connection
cursor.close()
connection.close()
