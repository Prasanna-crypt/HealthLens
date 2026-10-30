import sqlite3
conn = sqlite3.connect('healthlens.db')
c = conn.cursor()
c.execute("SELECT test_name, status, ai_explanation FROM test_results WHERE status = 'LOW' OR status = 'HIGH'")
rows = c.fetchall()
print(f'Found {len(rows)} HIGH/LOW rows.')
for row in rows[:5]:
    print(row)
