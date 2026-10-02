import bcrypt
hash_str = b'$2b$12$FOZfqBAkxjD2BwCgwrL.W.r2tYgZD4jFs0ww1GtqtcRy7HZ7xlwCy'
pw = b'bhavin252006'
print("Matches:", bcrypt.checkpw(pw, hash_str))
