import sqlite3 as sql

#connect sqlite to testcases database
con_testcases = sql.connect('db_TESTCASES.db')
cur_testcases = con_testcases.cursor()
# Drop testcases table if already exists
cur_testcases.execute("DROP TABLE IF EXISTS testcases")
sql_testcases = '''CREATE TABLE "testcases" (
    "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
    "NUM1" REAL,
    "NUM2" REAL,
    "Operation" TEXT,
    "RESULT" REAL
)'''
cur_testcases.execute(sql_testcases)
cur_testcases.execute("DROP TABLE IF EXISTS execution_results")
execution_results = '''CREATE TABLE "execution_results" (
    "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
    "NUM1"   REAL,
    "NUM2"   REAL,
    "OPERATION" TEXT,
    "RESULT" REAL,
    "EXPECTEDRESULT" REAL,
    "STATUS" TEXT
)'''
cur_testcases.execute(execution_results)
# Commit changes and close the connection for test cases
con_testcases.commit()
con_testcases.close()

#same operations for users database
con_users = sql.connect('db_USERS.db')
cur_users = con_users.cursor()
cur_users.execute("DROP TABLE IF EXISTS users")
cur_users.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')
con_users.commit()
con_users.close()
