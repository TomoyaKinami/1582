import sqlite3

dbname = 'number.sqlite3'
conn = sqlite3.connect(dbname)
cur = conn.cursor()

# terminalで実行したSQL文と同じようにexecute()に書く
cur.execute('SELECT * FROM number')

# 中身を全て取得するfetchall()を使って、printする。
member=cur.fetchall()

cur.close()
conn.close()

print(member[1][1])
print(eval('[0,1,2][0]'))