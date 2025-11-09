

import sqlite3 

db = sqlite3.connect('cards.db')
cur = db.cursor()

cur.execute(' SELECT name FROM sqlite_master WHERE type="table";')

tables = cur.fetchall()

cur.execute('select * from decks')
decks = cur.fetchall()

cur.execute('select * from cards')
cards = cur.fetchall()

for i in decks:
    print(i)

print()

for i in cards:
    print(i)
    
print()

for i in cur.execute('PRAGMA table_info("cards")').fetchall():
    print(i)

print()

for i in cur.execute('PRAGMA table_info("decks")').fetchall():
    print(i)
