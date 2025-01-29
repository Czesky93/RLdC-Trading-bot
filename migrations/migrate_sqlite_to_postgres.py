import sqlite3
import psycopg2

sqlite_db = "old_database.db"
postgres_db = "dbname"
postgres_user = "user"
postgres_password = "password"
postgres_host = "localhost"

sqlite_conn = sqlite3.connect(sqlite_db)
pg_conn = psycopg2.connect(dbname=postgres_db, user=postgres_user, password=postgres_password, host=postgres_host)

sqlite_cursor = sqlite_conn.cursor()
pg_cursor = pg_conn.cursor()

# Przykładowa migracja tabeli users
sqlite_cursor.execute("SELECT id, username, email FROM users")
users = sqlite_cursor.fetchall()
pg_cursor.executemany("INSERT INTO users (id, username, email) VALUES (%s, %s, %s)", users)

pg_conn.commit()
sqlite_conn.close()
pg_conn.close()
