import sqlite3 as  db
connection = db.connect("brainmap.db")
cursor = connection.cursor()

cursor.execute('''CREATE TABLE User
					(Name TEXT,
                          Emailid  TEXT,
                          Username TEXT,
                          Password TEXT,
                          Space INT,
                          Technology INT,
                          Environment INT,
                          Healthcare INT,
                          Credits INT,
					 PRIMARY KEY(Username)
					)
				''')


cursor.execute('''INSERT INTO User (Name,Emailid,Username,Password,Space,Technology,Environment,Healthcare,Credits) 
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
		''',['Joe','joe6161@gmail.com','joe','abc',1,1,0,0,30])

connection.commit()


connection.close()
