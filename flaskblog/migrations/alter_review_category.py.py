#from flask_sqlalchemy import create_engine
#to alter review table
import sqlite3


conn = sqlite3.connect("instance\site.db")
conn.execute("PRAGMA foreign_keys = off;") 
conn.execute("BEGIN TRANSACTION;") 
conn.execute("ALTER TABLE review_category RENAME TO review_category_old;") 
conn.execute("""
                  CREATE TABLE review_category(
                    review_id INTEGER,
                    category_id INTEGER,
                    FOREIGN KEY (review_id) REFERENCES review(id),
                    FOREIGN KEY (category_id) REFERENCES category(id)
                )

             """)
conn.execute("""
             INSERT INTO review_category SELECT * FROM review_category_old;
             """)
conn.execute("COMMIT;")
conn.execute("DROP TABLE review_category_old")
conn.execute("PRAGMA foreign_keys=on;")
conn.close()