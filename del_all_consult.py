import sqlite3
from tkinter import *
from tkinter import messagebox

def delete_all_records(password):
    # Votre mot de passe de permission
    correct_password = "votremotdepasse"

    # Vérifier si le mot de passe est correct
    if password == correct_password:
        try:
            # Connexion à la base de données
            conn = sqlite3.connect("cartographie.db")
            cursor = conn.cursor()

            # Exécuter la requête de suppression
            cursor.execute("DELETE FROM consultations")

            # Confirmer la suppression et enregistrer les modifications
            conn.commit()
            conn.close()

            messagebox.showinfo("Suppression réussie", "Tous les enregistrements ont été supprimés avec succès.")
        except sqlite3.Error as e:
            messagebox.showerror("Erreur de base de données", f"Erreur lors de la suppression : {e}")
    else:
        messagebox.showerror("Accès refusé", "Mot de passe incorrect. Vous n'avez pas la permission de supprimer les enregistrements.")

def open_password_dialog():
    # Créer une fenêtre pour demander le mot de passe
    password_window = Toplevel()
    password_window.title("Mot de passe requis")
    password_window.iconbitmap('.\img\salemgold.ico')

    # Centrer la fenêtre sur l'écran
    window_width = 300
    window_height = 150
    screen_width = password_window.winfo_screenwidth()
    screen_height = password_window.winfo_screenheight()

    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))
    password_window.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

    # Élément d'interface utilisateur pour le mot de passe
    Label(password_window, text="Mot de passe :").pack(pady=10)
    password_entry = Entry(password_window, show="*")
    password_entry.pack(pady=5)
    
    # Bouton pour soumettre le mot de passe
    submit_button = Button(password_window, text="Valider", command=lambda: handle_password_submit(password_entry.get()))
    submit_button.pack(pady=10)

    # Fonction pour traiter la soumission du mot de passe
    def handle_password_submit(password):
        delete_all_records(password)
        password_window.destroy()

    # Bloquer la fermeture de la fenêtre avec la croix
    password_window.protocol("WM_DELETE_WINDOW", lambda: None)

# Exemple d'utilisation : créer un bouton dans votre interface principale pour déclencher le processus
root = Tk()
root.title("Suppression de tous les enregistrements")
root.iconbitmap('.\img\salemgold.ico')

delete_button = Button(root, text="Supprimer tous les enregistrements", command=open_password_dialog)
delete_button.pack(padx=20, pady=20)

root.mainloop()
