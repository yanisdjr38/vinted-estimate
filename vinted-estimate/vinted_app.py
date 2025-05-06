import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, MULTIPLE
import os
import base64
import openai
from dotenv import load_dotenv

# Charger la clé API depuis .env
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Fonction d'encodage des images en base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Fonction principale d'appel à GPT-4 Vision
def generer_description():
    type_vetement = type_var.get()
    marque = marque_var.get()
    etat = etat_var.get()
    taille = taille_var.get()

    if not type_vetement or not marque or not etat or not taille:
        messagebox.showwarning("Champs manquants", "Merci de remplir tous les champs.")
        return

    if not photo_paths:
        messagebox.showwarning("Pas de photos", "Merci d'ajouter au moins une photo.")
        return

    prompt = f"""
Tu es un expert en vente de vêtements sur Vinted. Voici plusieurs photos d'un vêtement avec les informations suivantes :
- Type : {type_vetement}
- Marque : {marque}
- Taille : {taille}
- État : {etat}

Donne une estimation réaliste du prix en euros et rédige une description naturelle et attrayante pour l'annonce.
"""

    messages = [
        {"role": "user", "content": [{"type": "text", "text": prompt}] +
         [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(path)}"}} for path in photo_paths]
}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        description = response.choices[0].message.content
        description_text.delete("1.0", tk.END)
        description_text.insert(tk.END, description)
    except Exception as e:
        import traceback
        print("=== ERREUR DÉTAILLÉE ===")
        traceback.print_exc()
        messagebox.showerror("Erreur API", f"Une erreur est survenue : {e}")

# Ajouter des photos
def ajouter_photos():
    fichiers = filedialog.askopenfilenames(filetypes=[("Images", "*.png *.jpg *.jpeg")])
    for f in fichiers:
        if f not in photo_paths:
            photo_paths.append(f)
            photo_listbox.insert(tk.END, os.path.basename(f))

# Supprimer une photo sélectionnée
def supprimer_photo():
    selections = photo_listbox.curselection()
    for index in reversed(selections):
        photo_paths.pop(index)
        photo_listbox.delete(index)

# Copier la description
def copier_description():
    root.clipboard_clear()
    root.clipboard_append(description_text.get("1.0", tk.END))
    messagebox.showinfo("Copié", "Description copiée dans le presse-papiers.")

# Sauvegarder la description
def sauvegarder_description():
    contenu = description_text.get("1.0", tk.END)
    if not contenu.strip():
        messagebox.showwarning("Vide", "Aucune description à sauvegarder.")
        return

    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Fichier texte", "*.txt")])
    if filepath:
        with open(filepath, "w") as f:
            f.write(contenu)
        messagebox.showinfo("Sauvegardé", f"Description sauvegardée dans {filepath}")

# Interface
root = tk.Tk()
root.title("Estimateur Vinted avec GPT-4 Vision")
root.geometry("600x700")

photo_paths = []

# Type de vêtement
type_label = tk.Label(root, text="Type de vêtement")
type_label.pack()
type_var = tk.StringVar()
type_menu = tk.OptionMenu(root, type_var, "T-shirt", "Sweatshirt", "Pantalon", "Robe", "Veste", "Chaussures",
                          "Vêtement de sport", "Casquette", "Accessoire", "Sac à main", "Lunettes de soleil",
                          "Montre", "Bijoux", "Autre")
type_menu.pack()

# Marque
marque_label = tk.Label(root, text="Marque")
marque_label.pack()
marque_var = tk.StringVar()
marque_menu = tk.OptionMenu(root, marque_var, "Nike", "Adidas", "New Balance", "Levis", "Carharrt", "Puma",
                            "Converse", "Vans", "Stussy", "Supreme", "Gucci", "Chanel", "Balenciaga", "Dior",
                            "Lacoste", "Jordan", "North Face", "Moncler", "Yeezy", "Rick Owens", 
                            "Comme des Garçons", "Off-White", "A Bathing Ape", "Fear of God", 
                            "Palm Angels", "Stone Island", "Autre")
marque_menu.pack()

# État
etat_label = tk.Label(root, text="État")
etat_label.pack()
etat_var = tk.StringVar()
etat_menu = tk.OptionMenu(root, etat_var, "Neuf avec étiquette", "Très bon état", "Bon état")
etat_menu.pack()

# Taille
taille_label = tk.Label(root, text="Taille")
taille_label.pack()
taille_var = tk.StringVar()
taille_menu = tk.OptionMenu(root, taille_var, "S", "M", "L", "XL", "XXL", "Taille unique", "Autre")
taille_menu.pack()

# Photos
photo_button = tk.Button(root, text="Ajouter des photos", command=ajouter_photos)
photo_button.pack(pady=5)

photo_listbox = Listbox(root, selectmode=MULTIPLE, width=50)
photo_listbox.pack(pady=5)

delete_photo_button = tk.Button(root, text="Supprimer la/les photo(s) sélectionnée(s)", command=supprimer_photo)
delete_photo_button.pack(pady=5)

# Générer
gen_button = tk.Button(root, text="Générer description et estimation", command=generer_description)
gen_button.pack(pady=10)

# Zone de texte pour description
description_text = tk.Text(root, height=10, width=60)
description_text.pack(pady=5)

# Copier et sauvegarder
copy_button = tk.Button(root, text="Copier la description", command=copier_description)
copy_button.pack()

save_button = tk.Button(root, text="Sauvegarder dans un fichier", command=sauvegarder_description)
save_button.pack()

root.mainloop()
