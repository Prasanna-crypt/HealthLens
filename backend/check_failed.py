import sqlite3
conn = sqlite3.connect('healthlens.db')
c = conn.cursor()
c.execute("SELECT test_name, status FROM test_results WHERE ai_explanation LIKE '%Explanation unavailable due to error%'")
print('FAILED EXPLANATIONS:', c.fetchall())
