import sqlite3
import psycopg2

sqlite_db = "old_database.db"
postgres_db = "dbname"
postgres_user = "user"
postgres_password = "password"
postgres_host = "localhost"

try:
    sqlite_conn = sqlite3.connect(sqlite_db)
    pg_conn = psycopg2.connect(dbname=postgres_db, user=postgres_user, password=postgres_password, host=postgres_host)

    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()

    tables = ["users", "trades"]

    for table in tables:
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        columns = [desc[0] for desc in sqlite_cursor.description]
        rows = sqlite_cursor.fetchall()

        placeholders = ", ".join(["%s"] * len(columns))
        columns_str = ", ".join(columns)
        insert_query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"

        pg_cursor.executemany(insert_query, rows)
        print(f"Migrated {len(rows)} records from {table}")

    pg_conn.commit()
except Exception as e:
    print(f"Migration error: {e}")
finally:
    sqlite_conn.close()
    pg_conn.close()
