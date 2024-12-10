import sqlite3

def check_tables():

    conn = sqlite3.connect('C:/Users/hasou/OneDrive/Bureau/Cartographie/cartographie.db')
    cur = conn.cursor()
    
    #obtenir la liste des tables dans la base de données
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()


    #Afficher les tables trouvées

    if tables:
        print("Tables présentes dans la base de données :")
        for table in tables:
            print(table[0])
    else:
        print("Aucune table n'est présente dans la base de données.")

    conn.close()

check_tables()    
