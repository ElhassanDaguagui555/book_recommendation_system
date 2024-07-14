import sqlite3

def create_db():
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute('''
                  CREATE TABLE IF NOT EXISTS books (
                      id INTEGER PRIMARY KEY AUTOINCREMENT ,
                      title TEXT,
                      author TEXT,
                      genre TEXT,
                      year INTEGER NOT NULL,
                      description TEXT,
                      image TEXT
                  )
            ''')
        c.execute('''
                  CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY AUTOINCREMENT ,
                      username TEXT NOT NULL ,
                      password TEXT NOT NULL 
                  )
            ''')
        c.execute('''
                  CREATE TABLE IF NOT EXISTS recommandations (
                      id INTEGER PRIMARY KEY AUTOINCREMENT ,
                      user_id TEXT NOT NULL ,
                      book_id TEXT NOT NULL , 
                      FOREIGN KEY (user_id) REFERENCES users(id),
                      FOREIGN KEY (book_id) REFERENCES books(id)
                  )
            ''')
        
        
        conn.commit()
        conn.close()
        
if __name__ == '__main__' :
    create_db() 
        