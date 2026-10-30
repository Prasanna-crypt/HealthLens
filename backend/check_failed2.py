import sqlite3
conn = sqlite3.connect('healthlens.db')
c = conn.cursor()
c.execute("SELECT test_name, status FROM test_results WHERE ai_explanation LIKE '%Explanation unavailable%' AND status IN ('HIGH', 'LOW')")
print('REMAINING FAILURES:', c.fetchall())
