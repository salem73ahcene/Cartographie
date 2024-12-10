import sqlite3

def create_connection():
    conn = sqlite3.connect('cartographie.db')
    return conn

def read_emplacements():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM emplacements')
    emplacements = cur.fetchall()
    conn.close()
    return emplacements

def delete_emplacement(emplacement_id):
    """Supprime un emplacement de la base de données en fonction de l'ID."""
    conn = sqlite3.connect('cartographie.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Emplacements WHERE id = ?", (emplacement_id,))
    conn.commit()
    conn.close()
