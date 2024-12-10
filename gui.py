import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
import subprocess
import pandas as pd  # Pour l'exportation en Excel
import sys
from tkinter import Toplevel
from PIL import Image, ImageTk
import sys
import sqlite3
import os
from datetime import datetime
from fpdf import FPDF
from database import read_emplacements, delete_emplacement
#**********************************************************************************************************************
# Définition des couleurs pastel claires pour chaque emplacement
color_tags = {
        ("E001","E011","E021","E031","E041"): "#b3ffb3",  # Vert clair
        ("E002","E012","E022","E032","E042"): "#ffcccc",  # Rouge clair
        ("E003","E013","E023","E033","E043"): "#cce5ff",  # Bleu clair
        ("E004","E014","E024","E034","E044"): "#ffffcc",  # Jaune clair
        ("E005","E015","E025","E035","E045"): "#ffd9b3",  # Orange clair
        ("E006","E016","E026","E036","E046"): "#ffccf2",  # Rose clair
        ("E007","E017","E027","E037","E047"): "#e5ccff",  # Violet clair
        ("E008","E018","E028","E038","E048"): "#e6e6e6",  # Gris clair
        ("E009","E019","E029","E039","E049"): "#ccffdd",   # Menthe clair
        ("E010","E020","E030","E040","E050"): "#ffffcc"  # Jaune clair 
        
    }
#**********************************************************************************************************************
def get_color_for_emplacement(emplacement_code):
    """Retourne la couleur associée à un code d'emplacement."""
    for codes, color in color_tags.items():
        if emplacement_code in codes:
            return color
    return "#ffffff"  # Blanc par défaut si le code n'est pas trouvé

#***********************************************************************************************************************
# Fenêtre de connexion
# Variable globale pour suivre le mode de connexion

is_admin = False

def defilement():
    global text_position
    if text_position < -label.winfo_reqwidth():
        text_position = frame.winfo_width()
    else:
        text_position -= 2  # Ajustez la vitesse de défilement ici
    label.place(x=text_position, y=0)
    label.after(20, defilement)

def show_login_window(root):
    global is_admin, text_position, label, frame
    
    login_window = tk.Toplevel(root)
    login_window.title("Connexion")
    
    # Ajouter une icône à la fenêtre de connexion
    login_window.iconbitmap("./img/salemgold.ico")
    
    # Dimension de la fenêtre
    window_width = 1000
    window_height = 500  # Ajusté pour inclure la bande bleue
    
    # Récupérer la taille de l'écran
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    
    # Calcul pour centrer la fenêtre
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    
    # Appliquer la position et la taille
    login_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
    
    # Gestion de la fermeture de la fenêtre
    def on_close():
        """Ferme complètement l'application si la fenêtre de connexion est fermée."""
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter l'application ?"):
            sys.exit()  # Quitte l'application

    login_window.protocol("WM_DELETE_WINDOW", on_close)
    
    # Bande bleue avec texte défilant
    frame = tk.Frame(login_window, bg="blue", height=60)
    frame.pack(fill="x")
    
    message = "Bienvenue aux Archives CDE Annaba - Connexion au système"
    text_position = frame.winfo_width()
    
    # Créer le label pour le texte défilant
    label = tk.Label(frame, text=message, font=("Helvetica", 30), bg="blue", fg="white")
    frame.after(100, defilement)
    
    # Contenu de la fenêtre
    tk.Label(login_window, text="Choisissez un mode de connexion", font=('Helvetica', 12)).pack(pady=20)

    # Mode Admin
    tk.Button(login_window, text="Admin", font=('Helvetica', 16), bg="green", fg="white",
              command=lambda: admin_login(login_window, root)).pack(pady=5)

    # Mode Utilisateur
    tk.Button(login_window, text="Utilisateur", font=('Helvetica', 16), bg="green", fg="white",
              command=lambda: user_login(login_window, root)).pack(pady=5)

# Connexion admin
def admin_login(login_window, root):
    global is_admin
    is_admin = True
    login_window.destroy()  # Ferme la fenêtre de connexion
    ask_for_password(root)

# Connexion utilisateur
def user_login(login_window, root):
    global is_admin
    is_admin = False
    login_window.destroy()  # Ferme la fenêtre de connexion
    enable_user_mode(root)
    root.deiconify()  # Affiche la fenêtre principale pour l'utilisateur

# Demande de mot de passe pour l'admin
def ask_for_password(root):
    password_window = tk.Toplevel(root)
    password_window.title("Mot de passe admin")
    password_window.geometry("300x150")
    password_window.iconbitmap("./img/salemgold.ico")

    tk.Label(password_window, text="Entrez le mot de passe", font=('Helvetica', 12)).pack(pady=10)
    password_entry = tk.Entry(password_window, show='*', font=('Helvetica', 12))
    password_entry.pack(pady=5)
    global is_admin
    def check_password():
        global is_admin
        """Vérifie si le mot de passe est correct et active le mode admin si oui"""
        if password_entry.get() == "1234":
            is_admin = True
            password_window.destroy()
            root.deiconify()  # Affiche la fenêtre principale pour l'admin
        else:
            messagebox.showerror("Erreur", "Mot de passe incorrect")
            sys.exit()  # Quitte l'application en cas d'échec de connexion
             
    tk.Button(password_window, text="Valider", font=('Helvetica', 12), command=check_password).pack(pady=10)
     # Si l'utilisateur ferme la fenêtre, on quitte l'application
    
#************************************************************************************************************************    
# Désactiver les boutons non autorisés pour l'utilisateur
def enable_user_mode(root):
    for widget in root.winfo_children():
        if isinstance(widget, tk.Frame):  # Vérifie dans les frames enfants
            for child in widget.winfo_children():
                if isinstance(child, tk.Button) and child['text'] not in ["Afficher tout", "Afficher image", "Filtrer"]:
                    child.config(state='disabled')
#***********************************************************************************************************************
#Fonction pour ouvrir un autre executable
def open_other_exe():
    try:
        # Chemin vers le fichier .exe que tu souhaites exécuter
        subprocess.Popen(["./mov.exe"])
        messagebox.showinfo("Exécution", "Le programme a été lancé avec succès.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du lancement du programme : {str(e)}")
#************************************************************************************************************************
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


#************************************************************************************************************************
def confirm_close(add_window, root):
    """Demande confirmation avant de fermer la fenêtre après insertion."""
    if messagebox.askyesno("Confirmer", "Voulez-vous vraiment fermer cette fenêtre ?"):
        add_window.destroy()  # Ferme la fenêtre si l'utilisateur choisit "Oui"
    else:
        # Remettre la fenêtre d'ajout au premier plan
        add_window.grab_set()  # Empêche toute autre interaction jusqu'à la fermeture de la fenêtre d'ajout
        add_window.lift()  # Mettre la fenêtre d'ajout devant les autres
        add_window.focus_force()  # Forcer la fenêtre d'ajout à prendre le focus
        add_window.attributes('-topmost', True)  # Assure que la fenêtre est au-dessus de toutes les autres
        add_window.after(10, lambda: add_window.attributes('-topmost', False))  # Désactive '-topmost' après un court délai


#******************************************************************************************************************  
def extract_emplacement_code(emplacement):
    """Extrait la partie 'E###' de l'emplacement."""
    return emplacement.split('-')[0]  # Extrait tout avant le premier tiret
#*****************************************************************************************************************
# Fonction pour afficher les emplacements dans le Treeview
def display_emplacements(tree, record_count_textbox):
    """Récupère et affiche les emplacements depuis la base de données."""
    tree.delete(*tree.get_children())

    try:
        conn = sqlite3.connect('./cartographie.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM emplacements  ORDER BY id DESC" )
        rows = cursor.fetchall()

        for row in rows:
            # Extraire le code de l'emplacement et déterminer la couleur de la ligne
            emplacement_code = extract_emplacement_code(row[3])
            row_color = get_color_for_emplacement(emplacement_code)

            # Vérifier la validité de la convention (10 caractères)
            convention = row[1]
            if len(convention) != 10:
                tag_convention = f"convention_error"
                if not tree.tag_has(tag_convention):
                    tree.tag_configure(tag_convention, background="#8B0000", foreground="white")  # Rouge foncé
            else:
                tag_convention = f"normal_{emplacement_code}"
                if not tree.tag_has(tag_convention):
                    tree.tag_configure(tag_convention, background=row_color)

            # Insérer la ligne avec le tag approprié
            tree.insert('', 'end', values=row, tags=(tag_convention,))

        # Compter les enregistrements affichés
        count_records(tree, record_count_textbox)

    except sqlite3.Error as e:
        print(f"Erreur lors de l'accès à la base de données : {e}")

    finally:
        if conn:
            conn.close()


#**************************************************************************************************************************   
# Fonction pour filtrer les emplacements selon le texte de recherche
def filter_emplacements(tree, search_text, record_count_textbox):
    query = f"%{search_text}%"
    conn = sqlite3.connect('cartographie.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM emplacements 
        WHERE convention LIKE ? OR type LIKE ? OR emplacement LIKE ? OR intitule LIKE ? OR detenteur LIKE ? OR date_archive LIKE ? OR passation LIKE ? OR observation LIKE ?
    """, (query, query, query, query, query, query, query, query))
    emplacements = cursor.fetchall()

    for row in tree.get_children():
        tree.delete(row)

    for emplacement in emplacements:
        tree.insert('', 'end', values=emplacement)

    conn.close()
    # Mise à jour du compteur après le filtrage
    count_records(tree, record_count_textbox)  # Mise à jour du compteur

#**************************************************************************************************************************
def add_placeholder(entry, placeholder_text):
    """Ajoute un placeholder à un champ d'entrée."""
    entry.insert(0, placeholder_text)
    entry.config(fg='grey')

    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
            entry.config(fg='black')

    def on_focus_out(event):
        if entry.get() == '':
            entry.insert(0, placeholder_text)
            entry.config(fg='grey')

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
#**************************************************************************************************************************
# Fonction pour vérifier si les champs sont valides
def is_valid_entry(entry, placeholder_text):
    """Retourne True si le champ n'est pas vide et ne contient pas le placeholder."""
    return entry.get() != "" and entry.get() != placeholder_text

#*****************************************************************************************
def renover_bd():
    conn = sqlite3.connect('cartographie.db')
    cursor = conn.cursor()

    # Créer une nouvelle table temporaire pour stocker les données avec les IDs réorganisés
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emplacements_temp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            convention TEXT NOT NULL,
            type TEXT NOT NULL,
            emplacement TEXT NOT NULL,
            intitule TEXT NOT NULL,
            detenteur TEXT NOT NULL,
            date_archive DATE NOT NULL,
            passation TEXT NOT NULL,
            observation TEXT NOT NULL
        )
    ''')

    # Copier les données existantes dans la table temporaire
    cursor.execute('''
        INSERT INTO emplacements_temp (convention, type, emplacement, intitule, detenteur, date_archive, passation, observation)
        SELECT convention, type, emplacement, intitule, detenteur, date_archive, passation, observation FROM emplacements
    ''')

    # Supprimer l'ancienne table
    cursor.execute('DROP TABLE emplacements')

    # Renommer la table temporaire en l'ancienne table
    cursor.execute('ALTER TABLE emplacements_temp RENAME TO emplacements')

    conn.commit()
    conn.close()

    messagebox.showinfo("Succès", "Les IDs ont été réorganisés avec succès.")
#****************************************************************************************************************************
# Fonction d'ajout d'un emplacement (intégration de 'ajout_emplacement.py')
def open_ajout_emplacement_window():
    def insert_data():
        # Obtenir les valeurs des champs
        convention = entry_convention.get()
        type_emplacement = entry_type.get()
        emplacement = entry_emplacement.get()
        intitule = entry_intitule.get()
        detenteur = entry_detenteur.get()
        date_archive = entry_date.get()
        passation = entry_passation.get()
        observation = entry_observation.get()

            # Vérifier que les champs obligatoires ne sont pas vides
        if (convention != "0000 000 000 Entrez la Convention" and convention != "" and
            type_emplacement != "[DP/DR] Entrez le type" and type_emplacement != "" and
            emplacement != "E000-B000 Entrez l'emplacement" and emplacement != "" and
            intitule != "Entrez l'intitulé du projet" and intitule != "" and
            detenteur != "Entrez le Nom&Prénom de l'ingenieur" and detenteur != "" and
            date_archive != "Date d'archive finale dans la salle archive" and date_archive != "" and
            passation != "Il y a une passation [OUI/NON]" and passation != "" and
            observation != "Entrez l'observation [RAS s'il n y a pas]" and observation != ""):
          
            
            # Insertion des données dans la base de données
            conn = sqlite3.connect('cartographie.db')
            cursor = conn.cursor()
                
            cursor.execute('''INSERT INTO emplacements (convention, type, emplacement, intitule, detenteur, date_archive, passation, observation)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                            (convention, type_emplacement, emplacement, intitule, detenteur, date_archive, passation, observation))
                
            conn.commit()
            conn.close()

            # Confirmation et réinitialisation des champs
            messagebox.showinfo("Succès", "Les données ont été insérées avec succès.", parent=add_window)
            clear_fields()
            confirm_close(add_window, root)
        else:
            # Si l'un des champs n'est pas valide, affichez un message d'erreur
            add_window.grab_set()  # S'assurer que la fenêtre d'ajout reste active
            add_window.lift()  # Mettre la fenêtre d'ajout devant les autres
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs correctement.", parent=add_window)
            add_window.grab_release()  # Relâcher le contrôle après fermeture du message
       

    # Réinitialiser les champs du formulaire
    def clear_fields():
        entry_convention.delete(0, tk.END)
        entry_type.delete(0, tk.END)
        entry_emplacement.delete(0, tk.END)
        entry_intitule.delete(0, tk.END)
        entry_detenteur.delete(0, tk.END)
        entry_date.delete(0, tk.END)
        entry_passation.delete(0, tk.END)
        entry_observation.delete(0, tk.END)

    # Fenêtre secondaire pour l'ajout
    add_window = tk.Toplevel(root)
    add_window.title("Ajouter Emplacement")
    add_window.geometry('600x550')
    add_window.iconbitmap('.\img\salemgold.ico')
    # Assurer que la fenêtre d'ajout reste au premier plan lorsqu'elle est ouverte
    add_window.grab_set()  # Capture les interactions de l'utilisateur
    add_window.lift()  # Met la fenêtre d'ajout au-dessus des autres
    add_window.attributes('-topmost', True)  # Assure que la fenêtre d'ajout reste toujours au-dessus
    root.attributes('-topmost', False)  # Désactive le 'topmost' de la fenêtre principale
    # Définir la taille de la police
    font_size = 12
    font = ('Helvetica', font_size)
    #Créer un cadre pour le titre
    title_frame=tk.Frame(add_window, bg='blue', padx=20, pady=10)
    title_frame.pack(fill='x')
    # Ajouter un titre stylisé
    title_label = tk.Label(title_frame, text='Formulaire d\'insertion - Emplacement', font=('Helvetica', 16, 'bold'), fg='white', bg='blue')
    title_label.pack(fill='x')
    # Créer un cadre pour le formulaire
    form_frame = tk.Frame(add_window, padx=20, pady=20)
    form_frame.pack(fill='both', expand=True)


    # Labels et champs de saisie
    tk.Label(form_frame, text="Convention", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10, sticky='e')
    entry_convention = tk.Entry(form_frame, font=("Helvetica", 12), width=40)
    entry_convention.grid(row=0, column=1, padx=10, pady=10)
    add_placeholder(entry_convention, "0000 000 000 Entrez la Convention")

    tk.Label(form_frame, text="Type", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=10, sticky='e')
    entry_type = tk.Entry(form_frame, font=("Helvetica", 12), width=40)
    entry_type.grid(row=1, column=1, padx=10, pady=10)
    add_placeholder(entry_type, "[DP/DR] Entrez le type")

    tk.Label(form_frame, text="Emplacement", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=10, sticky='e')
    entry_emplacement = tk.Entry(form_frame, font=("Helvetica", 12), width=40)
    entry_emplacement.grid(row=2, column=1, padx=10, pady=10)
    add_placeholder(entry_emplacement, "E000-B000 Entrez l'emplacement")

    tk.Label(form_frame, text="Intitulé", font=("Helvetica", 12)).grid(row=3, column=0, padx=10, pady=10, sticky='e')
    entry_intitule = tk.Entry(form_frame, font=("Helvetica", 12), width=40)
    entry_intitule.grid(row=3, column=1, padx=10, pady=10)
    add_placeholder(entry_intitule, "Entrez l'intitulé du projet")

    tk.Label(form_frame, text="Détenteur", font=("Helvetica", 12)).grid(row=4, column=0, padx=10, pady=10, sticky='e')
    entry_detenteur = tk.Entry(form_frame, font=("Helvetica", 12), width=40)
    entry_detenteur.grid(row=4, column=1, padx=10, pady=10)
    add_placeholder(entry_detenteur, "Entrez le Nom&Prénom de l'ingenieur")

    tk.Label(form_frame, text="Date d'archive", font=("Helvetica", 12)).grid(row=5, column=0, padx=10, pady=10, sticky='e')
    entry_date = tk.Entry(form_frame, font=("Helvetica", 12), width=40)
    entry_date.grid(row=5, column=1, padx=10, pady=10)
    add_placeholder(entry_date, "Date d'archive finale dans la salle archive")

    tk.Label(form_frame, text="Passation", font=("Helvetica", 12)).grid(row=6, column=0, padx=10, pady=10, sticky='e')
    entry_passation = tk.Entry(form_frame, font=("Helvetica", 12), width=40)
    entry_passation.grid(row=6, column=1, padx=10, pady=10)
    add_placeholder(entry_passation, "Il y a une passation [OUI/NON]")

    tk.Label(form_frame, text="Observation", font=("Helvetica", 12)).grid(row=7, column=0, padx=10, pady=10, sticky='e')
    entry_observation = tk.Entry(form_frame, font=("Helvetica", 12), width=40)
    entry_observation.grid(row=7, column=1, padx=10, pady=10)
    add_placeholder(entry_observation, "Entrez l'observation [RAS s'il n y a pas]")

    # Boutons
    insert_button = tk.Button(add_window, text="Insérer", command=insert_data, font=("Helvetica", 12))
    insert_button.pack(side='left', padx=20, pady=10)
    Tooltip(insert_button, "Cliquez pour enregistrer!")
    close_button = tk.Button(add_window, text="Fermer", command=add_window.destroy, font=("Helvetica", 12))
    close_button.pack(side='right', padx=20, pady=10)
    Tooltip(close_button, "Cliquez pour annuler!")

#****************************************************************************************************************
def show_tooltip_for_row(event, tree):
    region = tree.identify_region(event.x, event.y)
    item = tree.identify_row(event.y)

    if region == "cell" and item:  # Si la souris est sur une ligne
        if not hasattr(tree, 'tooltip_window') or tree.tooltip_window is None:
            tree.tooltip_window = tk.Toplevel(tree)
            tree.tooltip_window.wm_overrideredirect(True)
            tree.tooltip_window.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tree.tooltip_window, text="Séléctionnez une ligne et double-cliquez pour supprimer", justify='left',
                             background="#ffffe0", relief='solid', borderwidth=1, font=("tahoma", "8", "normal"))
            label.pack(ipadx=1)
    else:
        if hasattr(tree, 'tooltip_window') and tree.tooltip_window:
            tree.tooltip_window.destroy()
            tree.tooltip_window = None


#****************************************************************************************************************
def delete_emplacement(id_):
    """Supprime l'emplacement dans la base de données."""
    conn = sqlite3.connect('cartographie.db')
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Emplacements WHERE id = ?", (id_,))
        conn.commit()
    except Exception as e:
        raise e
    finally:
        conn.close()

def delete_selected(tree):
    """Supprime l'élément sélectionné dans le Treeview."""
    selected_item = tree.selection()
    if selected_item:
        selected_data = tree.item(selected_item[0], 'values')
        response = messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cet enregistrement ?")
        if response:
            try:
                delete_emplacement(selected_data[0])  # Assure-toi que selected_data[0] est l'ID
                tree.delete(selected_item)
                messagebox.showinfo("Succès", "L'enregistrement a été supprimé avec succès.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur s'est produite lors de la suppression : {e}")
    else:
        messagebox.showwarning("Avertissement", "Veuillez sélectionner un enregistrement à supprimer.")

#def on_double_click(event):
#    """Gestion de l'événement double-clic pour supprimer un élément."""
#    tree = event.widget  # Récupérer le widget à l'origine de l'événement
#    delete_selected(tree)



def on_double_click(event, tree):
    global is_admin
    print(f"Double-click detected. is_admin: {is_admin}")  # Testez la valeur de is_admin
    
    """Gère le double-clic pour demander la suppression, seulement si c'est un admin."""
    if is_admin:  # Seuls les admins peuvent supprimer
        print("Admin: Suppression autorisée")
        tree = event.widget
        delete_selected(tree)
    else:
        messagebox.showwarning("Accès refusé", "Vous n'avez pas la permission de supprimer cet enregistrement.")

#**********************************************************************************************************************
# Fonction pour afficher une image en plein écran
from tkinter import Toplevel, Button, Label, Frame
from PIL import Image, ImageTk
def show_image():
    img_window = Toplevel()
    img_window.title("Salle d'archive")
    img_window.geometry("1020x600")
    img_window.iconbitmap('./img/salemgold.ico')

    # Créer une Frame globale pour le texte et le bouton
    control_frame = Frame(img_window, bg="yellow")
    control_frame.pack(fill="x", pady=10)

    # Titre de l'image (texte centré)
    title = Label(control_frame, text="Salle d'archive", font=("Helvetica", 22, "bold"), fg="red", bg="yellow")
    title.pack(side="left", padx=10)

    # Ajouter un bouton à droite du texte
    btn_info = Button(control_frame, text="Sur l'archivage", font=('Helvetica', 12),
                      bg='blue', fg='white', command=lambda: show_procedure(img_window))
    btn_info.pack(side="right", padx=10)
    Tooltip(btn_info, "Cliquez pour savoir plus sur l'archivage!!")

    # Vérification du chemin d'image
    img_path = "./img/Sallearchive.jpg"
    if not os.path.exists(img_path):
        print(f"Image non trouvée : {img_path}")
        return

    try:
        # Charger et afficher l'image
        img = Image.open(img_path)
        img = img.resize((1020, 500), Image.Resampling.LANCZOS)
        bg_image = ImageTk.PhotoImage(img)

        # Label pour l'image
        bg_label = tk.Label(img_window, image=bg_image)
        bg_label.pack(fill="both", expand=True)

        # Garder la référence de l'image pour éviter que le garbage collector ne la supprime
        bg_label.image = bg_image

    except Exception as e:
        print(f"Erreur lors du chargement de l'image : {e}")

    img_window.mainloop()

#****************************************************************************************************************************        

def show_procedure(parent_window):
    # Fonction pour afficher la fenêtre avec la procédure d'archivage
    procedure_window = Toplevel(parent_window)
    procedure_window.title("Procédure d'archivage")
    procedure_window.geometry("600x400")
    procedure_window.iconbitmap('./img/salemgold.ico')

    procedure_text = tk.Text(procedure_window, wrap='word', font=("Helvetica", 12), padx=10, pady=10)
    procedure_text.pack(fill='both', expand=True)

    # Activer temporairement le widget Text pour insérer du contenu
    procedure_text.config(state='normal')

    # Texte explicatif sur la procédure d'archivage
    procedure_text.insert(tk.END, """
    Procédure d'archivage :

                                                     Procédure d'Archivage selon les Recommandations de CTC

Pour procéder à l'archivage d'un dossier, il est impératif de suivre les étapes suivantes :

Vérification de la Numérisation : Assurez-vous que tous les documents contenus dans le dossier sont dûment numérisés. Il est formellement interdit d'archiver un dossier qui contient des documents non numérisés, afin de garantir l'intégrité et l'accessibilité des informations.

Association des Documents : Lorsque cela est possible, associez le dossier administratif aux plans de la même convention. Cette association est essentielle, notamment lorsque le volume des plans le nécessite.

Établissement d'un Document de Passation : Un document de "Passation" ou de "Décharge" doit être établi entre l'ingénieur et le responsable de l'archivage, sous la supervision du directeur de l'agence. Ce document permettra de définir clairement les responsabilités de chacun dans le processus d'archivage.

Conditionnement des Dossiers : Placez le dossier dans une boîte numérotée, en y inscrivant un index spécifique. Cette étape facilite l'identification et le suivi des dossiers archivés.

Emplacement de Stockage : Disposez la boîte dans son emplacement dédié, situé sur un support d'étagère pré-indexé. Cette organisation est cruciale pour optimiser l'espace et la gestion des archives.
Inscription dans l'Application de Cartographie : Toutes les informations relatives à l'archivage doivent être inscrites dans l'application "Cartographie". Cette application a pour objectif de faciliter la navigation dans les archives.
Gestion des consultation:Afin de gérer la consultation et l'exploitation des dossiers archivés il impératif de concevoir une méthode qui organise les entrées et les sorties pour but d'assurer la traçabilité des dossuers, qu'ils soient consultés dans la salle d'archives ou en dehors.

En suivant ces recommandations, CTC garantit un archivage efficace et conforme aux normes en vigueur, assurant ainsi la pérennité et l'intégrité des documents archivés.


    """)

    # Désactiver le widget Text après l'insertion
    procedure_text.config(state='disabled')
#****************************************************************************************************************************
def export_to_excel(tree):
    """Exporte les données de la Treeview vers un fichier Excel."""
    # Créer une liste de dictionnaires pour stocker les données
    data = []
    for row_id in tree.get_children():
        row_values = tree.item(row_id)['values']
        data.append({
            'ID': row_values[0],
            'Convention': row_values[1],
            'Type': row_values[2],
            'Emplacement': row_values[3],
            'Intitulé': row_values[4],
            'Détenteur': row_values[5],
            'Date Archive': row_values[6],
            'Passation': row_values[7],
            'Observation': row_values[8]
        })

    # Convertir la liste en DataFrame
    df = pd.DataFrame(data)

    # Sauvegarder en Excel
    file_path = "D:/emplacement/emplacements.xlsx"
    df.to_excel(file_path, index=False)

    messagebox.showinfo("Exportation Excel", f"Les données ont été exportées avec succès vers {file_path}")



#*****************************************************************************************************************************
import tkinter as tk
from tkinter import Toplevel, Label, Entry, Button, messagebox

def ask_for_input(title, prompt, icon_path=None):
    def on_submit():
        nonlocal input_value  # Rendre la variable modifiable dans la fonction
        input_value = input_field.get()
        if input_value.strip():  # Si l'utilisateur entre une valeur
            window.destroy()  # Fermer la fenêtre si une valeur est donnée
        else:
            messagebox.showwarning("Champ requis", "Ce champ est obligatoire.")  # Message d'erreur si vide

    # Créer une nouvelle fenêtre
    window = Toplevel()
    window.title(title)
    

    # Définir l'icône pour la fenêtre
    if icon_path:
        window.iconbitmap(icon_path)

    # Définir la taille de la fenêtre (par exemple, 400x150)
    window_width = 400
    window_height = 150

    # Obtenir la taille de l'écran
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculer la position pour centrer la fenêtre
    position_x = (screen_width // 2) - (window_width // 2)
    position_y = (screen_height // 2) - (window_height // 2)

    # Appliquer la taille et la position de la fenêtre
    window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
    window.resizable(False, False)


    # Ajouter les éléments graphiques
    label = Label(window, text=prompt)
    label.pack(pady=10)

    input_field = Entry(window, width=40)
    input_field.pack(pady=5)

    submit_button = Button(window, text="Valider", command=on_submit)
    submit_button.pack(pady=10)

    input_value = None  # Initialiser la variable pour stocker la valeur entrée

    window.grab_set()  # Empêcher l'interaction avec la fenêtre principale tant que la boîte de dialogue est ouverte
    window.wait_window()  # Attendre la fermeture de la fenêtre

    return input_value  # Retourner la valeur entrée après la fermeture de la fenêtre



#****************************************************************************************************************************
# Création d'un PDF contient la liste des emplacements des Dossiers
# Variables globales pour stocker le nom et le titre, à définir une seule fois
from fpdf import FPDF
import os
from datetime import datetime
from tkinter import messagebox

archiviste_name = None
report_title = None
def generate_pdf(tree):
    global archiviste_name, report_title

    # Chemin de l'icône
    icon_path = "./img/salemgold.ico"

    # Chemin du dossier pour stocker le PDF
    folder_path = "D:/emplacement/"

    # Vérifier si le dossier existe, sinon le créer
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)

    # Demander les informations une seule fois, avec validation obligatoire
    if archiviste_name is None or archiviste_name.strip() == "":
        archiviste_name = ask_for_input("Nom de l'archiviste", "Veuillez entrer le nom de l'archiviste :", icon_path)

    if report_title is None or report_title.strip() == "":
        report_title = ask_for_input("Titre du rapport", "Le Nom de Votre Agence SVP! :", icon_path)

    # Génération du PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Définir la police pour l'en-tête (police plus grande pour l'en-tête)
    pdf.set_font("Arial", size=10)

    # Obtenez la date et l'heure actuelles
    current_datetime = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Créez une ligne pour l'en-tête
    pdf.cell(0, 10, txt=f"L'Archiviste: {archiviste_name}", ln=False)
    pdf.cell(0, 10, txt=f"Date et Heure: {current_datetime}", ln=True, align='R')

    # Titre du rapport
    full_title = f"Emplacements des Dossiers Archivés de l'agence {report_title}"
    pdf.cell(200, 10, txt=full_title, ln=True, align='C')

    # Ajuster la taille de la police pour le corps du texte
    pdf.set_font("Arial", size=8)

    # Ajouter une ligne avec les mots clés
    pdf.cell(0, 10, txt="Mots clés : CV = Convention, Dét = Détenteur, T = Type, Empl = Emplacement, Intit = Intitulé, Date = Date Archive, Pass = Passation, Obs = Observation", ln=True, align='L')

    # Largeurs de colonnes ajustées
    col_widths = {
        'id': 10, 'convention': 18, 'type': 6,
        'emplacement': 16, 'intitule': 60, 'détenteur': 25,
        'date_archive': 18, 'passation': 8, 'observation': 30,
    }

    headers = ['ID', 'Conv.', 'T.', 'Empl.', 'Intit.', 'Dét.', 'Date', 'Pass.', 'Obs.']
    for i, header in enumerate(headers):
        pdf.cell(list(col_widths.values())[i], 10, header, 1)

    pdf.ln()

    # Fonction pour gérer le texte long
    def get_line_height(text, col_width, line_spacing):
        """Calcule la hauteur en fonction du texte et de la largeur de la colonne."""
        num_lines = len(pdf.multi_cell(col_width, 10, text, split_only=True))  # Compte le nombre de lignes
        return num_lines * 5  # Retourne la hauteur basée sur le nombre de lignes

    # Définir l'espacement vertical réduit pour les textes longs
    line_spacing = 5  # Ajustez cette valeur pour réduire l'espacement

    for row_id in tree.get_children():
        row_values = tree.item(row_id)['values']

        # Obtenir le texte de chaque cellule
        intitule_text = str(row_values[4])
        observation_text = str(row_values[8])

        # Calculer les hauteurs de "intitulé" et "observation" en fonction du texte
        intitule_height = get_line_height(intitule_text, col_widths['intitule'], line_spacing)
        observation_height = get_line_height(observation_text, col_widths['observation'], line_spacing)

        # Hauteur maximale de la ligne (la plus grande entre les deux)
        max_line_height = max(intitule_height, observation_height, 5)

        # Vérification avant d'ajouter une nouvelle page si nécessaire
        if pdf.get_y() + max_line_height > 275:  # Ajuster cette valeur si nécessaire
            pdf.add_page()

        # Fixer la position Y avant d'écrire quoi que ce soit
        current_y = pdf.get_y()

        # Cellule "id"
        pdf.cell(col_widths['id'], max_line_height, str(row_values[0]), 1)

        # Cellule "convention"
        pdf.cell(col_widths['convention'], max_line_height, str(row_values[1])[:12], 1)  # Tronquer si nécessaire

        # Cellule "type"
        pdf.cell(col_widths['type'], max_line_height, str(row_values[2]), 1)

        # Cellule "emplacement"
        pdf.cell(col_widths['emplacement'], max_line_height, str(row_values[3]), 1)

        # Multi-cellule pour "intitulé" (ajuster si texte court)
        x_pos = pdf.get_x()  # Sauvegarder la position X
        y_pos = current_y    # Utiliser la position Y sauvegardée

        if intitule_height < max_line_height:
            # Si le texte de "intitulé" est court, forcer l'affichage avec une hauteur de ligne fixe
            pdf.multi_cell(col_widths['intitule'], max_line_height, intitule_text, 1)
        else:
            # Si le texte de "intitulé" est long, utiliser le line_spacing
            pdf.multi_cell(col_widths['intitule'], line_spacing, intitule_text, 1)

        pdf.set_xy(x_pos + col_widths['intitule'], y_pos)  # Réaligner après

        # Cellule "détenteur"
        pdf.cell(col_widths['détenteur'], max_line_height, str(row_values[5]), 1)

        # Cellule "date_archive"
        pdf.cell(col_widths['date_archive'], max_line_height, str(row_values[6]), 1)

        # Cellule "passation"
        pdf.cell(col_widths['passation'], max_line_height, str(row_values[7]), 1)

        # Multi-cellule pour "observation" (ajuster si texte court)
        x_pos = pdf.get_x()
        y_pos = current_y    # Utiliser la même position Y

        if observation_height < max_line_height:
            # Si le texte de "observation" est court, forcer l'affichage avec une hauteur de ligne fixe
            pdf.multi_cell(col_widths['observation'], max_line_height, observation_text, 1)
        else:
            # Si le texte de "observation" est long, utiliser le line_spacing
            pdf.multi_cell(col_widths['observation'], line_spacing, observation_text, 1)

        pdf.set_xy(x_pos + col_widths['observation'], y_pos)

        # Saut de ligne pour la prochaine ligne
        pdf.ln(max_line_height)

    # Enregistrer le fichier PDF dans le dossier spécifié
    pdf_file = os.path.join(folder_path, "emplacements.pdf")
    pdf.output(pdf_file)
    os.startfile(pdf_file)  # Ouvre le fichier PDF (Windows uniquement)
    messagebox.showinfo("Impression", "Le fichier PDF a été généré ; trouvez-le dans D:/emplacement/")

#*****************************************************************************************************************************    

# Fonction de modification d'un emplacement (intégration de 'modif.py')
def run_modif_emplacement(selected_data):
    if selected_data:
        # Appeler directement la fenêtre de modification ici
        edit_selected(tree)
    else:
        messagebox.showwarning("Avertissement", "Veuillez sélectionner un enregistrement à modifier.")
   
    
# Récupérer la ligne sélectionnée et appeler la fonction pour modifier
def edit_selected(tree):
    selected_item = tree.selection()
    if selected_item:
        selected_data = tree.item(selected_item[0], 'values')
        start_modification_form(selected_data)
    else:
        messagebox.showwarning("Avertissement", "Veuillez sélectionner une ligne à modifier.")

#******************************************************************************************************************   
def confirm_close(root):
    """Demande confirmation avant de fermer la fenêtre après modification."""
    if messagebox.askyesno("Confirmer", "Voulez-vous vraiment fermer cette fenêtre après la modification ?"):
        root.destroy()  # Ferme la fenêtre si l'utilisateur choisit "Oui"
    # Si l'utilisateur choisit "Non", rien ne se pass

#****************************************************************************************************************** 
def update_emplacement(id_, convention, type_, emplacement, intitule, detenteur, date_archive, passation, observation, root):
    """Met à jour un emplacement dans la base de données."""
    conn = sqlite3.connect('cartographie.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE emplacements
            SET convention = ?, type = ?, emplacement = ?, intitule = ?, detenteur = ?, date_archive = ?, passation = ?, observation = ?
            WHERE id = ?
        """, (convention, type_, emplacement, intitule, detenteur, date_archive, passation, observation, id_))
        conn.commit()
        messagebox.showinfo("Succès", "L'emplacement a été modifié avec succès.")
        confirm_close(root)
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")
    finally:
        conn.close()

def start_modification_form(selected_data):
    """Affiche le formulaire avec les données sélectionnées pour modification."""
    root = tk.Tk()
    root.title("Modifier Emplacement")
    root.geometry("600x400")
    root.iconbitmap('.\img\salemgold.ico')
    style = ttk.Style()
    style.configure("Treeview", font=("Helvetica", 12))  # Police de 14 pour les cellules
    style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))  # Police pour l'en-têt
    # Extraction des données passées en argument
    id_ = selected_data[0]
    convention = selected_data[1]
    type_ = selected_data[2]
    emplacement = selected_data[3]
    intitule = selected_data[4]
    detenteur = selected_data[5]
    date_archive = selected_data[6]
    passation = selected_data[7]
    observation = selected_data[8]

    # Création du titre
    title_label = tk.Label(
        root, text="Modifier Emplacement", font=("Helvetica", 24, "bold"), 
        fg="white", bg="blue", pady=10
    )
    title_label.pack(fill='x')

    # Création des champs du formulaire
    form_frame = tk.Frame(root, padx=20, pady=10)
    form_frame.pack(fill='both', expand=True)

    tk.Label(form_frame, text="Convention", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5, sticky='e')
    entry_convention = tk.Entry(form_frame, width=60)
    entry_convention.grid(row=0, column=1, padx=10, pady=5)
    entry_convention.insert(0, convention)

    tk.Label(form_frame, text="Type", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5, sticky='e')
    entry_type = tk.Entry(form_frame, width=60)
    entry_type.grid(row=1, column=1, padx=10, pady=5)
    entry_type.insert(0, type_)

    tk.Label(form_frame, text="Emplacement", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=5, sticky='e')
    entry_emplacement = tk.Entry(form_frame, width=60)
    entry_emplacement.grid(row=2, column=1, padx=10, pady=5)
    entry_emplacement.insert(0, emplacement)

    tk.Label(form_frame, text="Intitulé", font=("Helvetica", 12)).grid(row=3, column=0, padx=10, pady=5, sticky='e')
    entry_intitule = tk.Entry(form_frame, width=60)
    entry_intitule.grid(row=3, column=1, padx=10, pady=5)
    entry_intitule.insert(0, intitule)

    tk.Label(form_frame, text="Détenteur", font=("Helvetica", 12)).grid(row=4, column=0, padx=10, pady=5, sticky='e')
    entry_detenteur = tk.Entry(form_frame, width=60)
    entry_detenteur.grid(row=4, column=1, padx=10, pady=5)
    entry_detenteur.insert(0, detenteur)

    tk.Label(form_frame, text="Date Archive", font=("Helvetica", 12)).grid(row=5, column=0, padx=10, pady=5, sticky='e')
    entry_date_archive = tk.Entry(form_frame, width=60)
    entry_date_archive.grid(row=5, column=1, padx=10, pady=5)
    entry_date_archive.insert(0, date_archive)

    tk.Label(form_frame, text="Passation", font=("Helvetica", 12)).grid(row=6, column=0, padx=10, pady=5, sticky='e')
    entry_passation = tk.Entry(form_frame, width=60)
    entry_passation.grid(row=6, column=1, padx=10, pady=5)
    entry_passation.insert(0, passation)

    tk.Label(form_frame, text="Observation", font=("Helvetica", 12)).grid(row=7, column=0, padx=10, pady=5, sticky='e')
    entry_observation = tk.Entry(form_frame, width=60)
    entry_observation.grid(row=7, column=1, padx=10, pady=5)
    entry_observation.insert(0, observation)

    # Créer un cadre pour les boutons
    button_frame = tk.Frame(root, padx=20, pady=10)
    button_frame.pack(fill='x')

    # Ajouter les boutons dans le cadre, placés à gauche et à droite
    btn_modif = tk.Button(
        button_frame, text="Modifier", font=("Helvetica", 12), 
        command=lambda: update_emplacement(
           id_, 
            entry_convention.get(), 
            entry_type.get(), 
            entry_emplacement.get(),
            entry_intitule.get(),  # Correction ici
            entry_detenteur.get(), 
            entry_date_archive.get(),
            entry_passation.get(),  # Correction ici
            entry_observation.get(),
            root                        #passer la fenêtre pour la fermeture
        )
    )
    btn_modif.pack(side='left', padx=10)
    Tooltip(btn_modif, "Cliquez pour enregistrer les modifications")

    btn_cancel = tk.Button(button_frame, text="Annuler", font=("Helvetica", 12), command=root.destroy)
    btn_cancel.pack(side='right', padx=10)
    Tooltip(btn_cancel, "Cliquez pour annuler")

    root.mainloop()  

#******************************************************************************************************************    

#L'interface Principale

def start_application(user_mode=False):
    global is_admin
    global root
    root = tk.Tk()
    root.title("Affichage des Emplacements")
    root.geometry('1680x1000')
    root.iconbitmap('./img/salemgold.ico')  # Ajout de l'icône
      # Cacher la fenêtre principale
    root.withdraw()
     # Afficher la fenêtre de connexion
    show_login_window(root)
    # Ajout d'un label pour personnaliser le "titre"
    title_label = tk.Label(
        root, 
        text="CARTOGRAPHIE D'ARCHIVE CTC-CDE ANNABA", 
        font=("Helvetica", 18, "bold"), 
        fg="white", 
        bg="blue", 
        pady=10
    )
    title_label.pack(fill='x')
    
    style = ttk.Style()
    style.configure("Treeview", font=("Helvetica", 11))  # Police de 14 pour les cellules
    style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))  # Police pour l'en-tête
    
    # Cadre supérieur pour les boutons et la recherche, avec fond bleu
    top_frame = tk.Frame(root, padx=10, pady=10, bg='blue')  # Ajout du bg='blue'
    top_frame.pack(side='top', fill='x')

    tk.Label(top_frame, text="Recherche :", font=('Helvetica', 12), bg='blue', fg='white').grid(row=0, column=0, padx=10)
    entry_search = tk.Entry(top_frame, font=('Helvetica', 14), width=20)
    entry_search.grid(row=0, column=1, padx=10)

    # Bouton Filtrer
    btn_filter = tk.Button(top_frame, text="Filtrer", command=lambda: filter_emplacements(tree, entry_search.get(), record_count_textbox), 
                        font=('Helvetica', 12), bg='black', fg='white')
    btn_filter.grid(row=0, column=2, padx=10)
    Tooltip(btn_filter, "Cliquez pour filtrer les emplacements")

    # Bouton Ajouter Emplacement
    btn_add = tk.Button(top_frame, text="Nouveau", command=open_ajout_emplacement_window, 
                        font=('Helvetica', 12), bg='black', fg='white')
    btn_add.grid(row=0, column=3, padx=10)
    Tooltip(btn_add, "Cliquez pour ajouter un emplacement")


    # Bouton Afficher tout
    btn_show = tk.Button(top_frame, text="Afficher tout", command=lambda: display_emplacements(tree, record_count_textbox), 
                        font=('Helvetica', 12), bg='black', fg='white')
    btn_show.grid(row=0, column=4, padx=10)
    Tooltip(btn_show, "Cliquez pour afficher tous les emplacements")


    # Bouton Imprimer PDF
    # Charger l'image pour le bouton
    pdf_img = Image.open('./img/pdf.png')
    pdf_img = pdf_img.resize((30, 25), Image.LANCZOS)
    pdf_photo = ImageTk.PhotoImage(pdf_img)
    btn_print = tk.Button(top_frame, image=pdf_photo, command=lambda: generate_pdf(tree), bg='white')
    btn_print.grid(row=0, column=5, padx=10)
    Tooltip(btn_print, "Cliquez pour imprimer les emplacements en PDF")
    btn_print.image = pdf_photo 
    # Bouton Exporter en Excel
    # Charger l'image pour le bouton
    excel_img = Image.open('./img/excel.png')
    excel_img = excel_img.resize((30, 25), Image.LANCZOS)
    excel_photo = ImageTk.PhotoImage(excel_img)

    btn_excel = tk.Button(top_frame, image=excel_photo, command=lambda: export_to_excel(tree), bg='white')
    btn_excel.grid(row=0, column=6, padx=10)
    Tooltip(btn_excel, "Cliquez pour exporter les emplacements en Excel")
    # Conserver la référence à l'image pour que Python ne la libère pas
    btn_excel.image = excel_photo

    # Bouton Modifier
    btn_edit = tk.Button(top_frame, text="Modifier", command=lambda: edit_selected(tree), 
                        font=('Helvetica', 12), bg='black', fg='white')
    btn_edit.grid(row=0, column=7, padx=10)
    Tooltip(btn_edit, "Cliquez pour modifier l'emplacement sélectionné")

    # Bouton Afficher Image
    btn_img = tk.Button(top_frame, text="Afficher Image", font=('Helvetica', 12), 
                        command=show_image, bg='black', fg='white')
    btn_img.grid(row=0, column=8, padx=10)
    Tooltip(btn_img, "Cliquez pour afficher l'image de l'emplacement sélectionné")

    # Bouton pour Rénover les IDs de la table emplacements
    btn_renover = tk.Button(top_frame, text="Rénover la BD", command=renover_bd,
                        font=('Helvetica', 12), bg='black', fg='white')
    btn_renover.grid(row=0, column=9, padx=10)  # Ajoutez ce bouton à la grille ou là où vous le souhaitez
    Tooltip(btn_renover, "Cliquez pour rénover les IDs de la table")

    # Ajouter ce bouton dans ton interface
    btn_open_exe = tk.Button(top_frame, text="gestion", command=open_other_exe,
                       font=('Helvetica', 12), bg='black', fg='white')
    btn_open_exe.grid(row=0, column=10, padx=10) # Ajuster la disposition du bouton selon ton interface
    Tooltip(btn_open_exe, "Gérer les consultations des dossiers")

    
    # Ajoutez ici votre code pour créer 'record_count_textbox' et l'ajouter à l'interface
    record_count_textbox = tk.Entry(top_frame, width=5, font=("Helvetica", 12))
    record_count_textbox.grid(row=0, column=11, padx=10)  # Utiliser grid au lieu de pack
    #***********************************************************************************************************************
    # Configuration de la Treeview avec Scrollbar
    tree_frame = tk.Frame(root)  # Crée un Frame pour contenir la Treeview et la Scrollbar
    tree_frame.pack(fill='both', expand=True, padx=10, pady=10)  # Place le Frame

    # Créer la Scrollbar verticale
    scrollbar_y = tk.Scrollbar(tree_frame, orient='vertical')
    scrollbar_y.pack(side='right', fill='y')  # Place la Scrollbar à droite

    # Créer la Treeview
    columns = (
        'id', 'convention', 'type', 'emplacement', 
        'intitule', 'detenteur', 'date_archive', 'passation', 'observation'
    )
    tree = ttk.Treeview(
        tree_frame, columns=columns, show='headings', yscrollcommand=scrollbar_y.set
    )

    # Configurer la Scrollbar pour suivre le mouvement de la Treeview
    scrollbar_y.config(command=tree.yview) 
    #************************************************************************************************************************ 
    # Configuration de Treeview
    # columns = ('id', 'convention', 'type', 'emplacement', 'intitule', 'detenteur', 'date_archive', 'passation', 'observation')
    #tree = ttk.Treeview(root, columns=columns, show='headings')

    tree.heading('id', text='ID')
    tree.column('id', width=2)
    tree.heading('convention', text='Convention')
    tree.column('convention', width=15)
    tree.heading('type', text='Type')
    tree.column('type', width=2)
    tree.heading('emplacement', text='Emplace')
    tree.column('emplacement', width=15)
    tree.heading('intitule', text='Intitulé')
    tree.column('intitule', width=550)
    tree.heading('detenteur', text='Détenteur')
    tree.column('detenteur', width=50)
    tree.heading('date_archive', text='Date')
    tree.column('date_archive', width=30)
    tree.heading('passation', text='Passat')
    tree.column('passation', width=4)
    tree.heading('observation', text='Obs')
    tree.column('observation', width=40)

    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col)


    # Configuration des tags
    for key, color in color_tags.items():
        tree.tag_configure(f"tag_{key}", background=color)

    tree.tag_configure("tag_default", background="#ffffff")  # Blanc par défaut

    tree.pack(fill='both', expand=True)
   
    # Appeler display_emplacements pour charger les données et ensuite compter les enregistrements
    display_emplacements(tree, record_count_textbox)
    count_records(tree, record_count_textbox)  # Compter les enregistrements après l'affichage des données
    global is_admin
     # Bind the double-click event only if is_admin is True
   
    tree.bind("<Double-1>", lambda event: on_double_click(event, tree))
     # Lier l'evenement de l'info_bulles sur une ligne de la treeview
    tree.bind("<Motion>", lambda event: show_tooltip_for_row(event, tree))

    root.mainloop()

def count_records(tree, record_count_textbox):
    """Comptez les enregistrements dans le Treeview et mettez à jour le textbox."""
    num_records = len(tree.get_children())
    record_count_textbox.delete(0, tk.END)  # Effacer le contenu actuel
    record_count_textbox.insert(0, str(num_records))  # Insérer le nombre d'enregistrements
#********************************************************************************************************************"
def get_color_for_emplacement(emplacement_code):
    """Retourne la couleur associée à un code d'emplacement."""
    for codes, color in color_tags.items():
        if emplacement_code in codes:
            return color
    return "#ffffff"  # Blanc par défaut si le code n'est pas trouvé
#**********************************************************************************************************************
def get_color_for_emplacement(emplacement_code):
    """Retourne la couleur associée à un code d'emplacement."""
    for codes, color in color_tags.items():
        if emplacement_code in codes:
            return color
    return "#ffffff"  # Blanc par défaut si le code n'est pas trouvé


#**************************************************************************************************************************************
if __name__ == '__main__':
    start_application()

   