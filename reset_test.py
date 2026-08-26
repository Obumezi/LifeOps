import sqlite3

connection = sqlite3.connect("database/lifeops.db")

connection.execute("DELETE FROM agent_decisions")
connection.execute("DELETE FROM payment_transactions")
connection.execute(
    "UPDATE tasks SET status = ?",
    ("pending",)
)

connection.commit()
connection.close()

print("LifeOps test environment reset successfully.")