import sqlite3

def create_database():

    conn = sqlite3.connect('cartographie.db')
    cur = conn.cursor()
    
    #Création de latable "emplacements"
   
    cur.execute('''CREATE TABLE IF NOT EXISTS emplacements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        convention TEXT NOT NULL,
        type TEXT NOT NULL,
        emplacement TEXT NOT NULL,
        intitule TEXT NOT NULL,
        detenteur TEXT NOT NULL,
        date_archive DATE NOT NULL,
        passation TEXT NOT NULL,
        observation TEXT NOT NULL
    ) ''')
   

    # Creation de la table "User"
    cur.execute('''CREATE TABLE IF NOT EXISTS User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
    ) ''')


     # sauvegarder les changements
    conn.commit()
    # fermer la connexion
    conn.close()

    # Executer la fonction pour créer la base de données et les tables
create_database()