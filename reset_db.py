import sqlite3

DB_PATH = "database/lifeops.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Remove previous LifeOps decisions
cursor.execute("DELETE FROM agent_decisions")

# Remove previous payment transactions
cursor.execute("DELETE FROM payment_transactions")

# Return every bill to pending
cursor.execute("""
    UPDATE tasks
    SET status = 'pending'
""")

conn.commit()
conn.close()

print("LifeOps test environment reset successfully.")