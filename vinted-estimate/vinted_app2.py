import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, MULTIPLE, PhotoImage, ttk
import os
import base64
import openai
from dotenv import load_dotenv

# Charger la clé API
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Fonction d'encodage des images
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Fonction principale GPT-4o
def generer_description():
    if not photo_paths:
        messagebox.showwarning("Pas de photos", "Merci d'ajouter au moins une photo.")
        return

    prompt = """
Tu es un expert en vente de vêtements sur Vinted.
Analyse uniquement les photos et détecte :
- Type de vêtement
- Marque (si identifiable)
- Taille (si visible)
- État (neuf, très bon état, bon état, usé)
- Une estimation du prix en euros.
Rédige une description naturelle et attrayante pour l'annonce.
"""

    messages = [
        {
            "role": "user",
            "content": (
                [{"type": "text", "text": prompt}]
                + [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(path)}"}} for path in photo_paths]
            )
        }
    ]

    gen_button.config(state=tk.DISABLED, text="Analyse en cours...")
    root.update()

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        description = response.choices[0].message.content
        description_text.delete("1.0", tk.END)
        description_text.insert(tk.END, description)
    except Exception as e:
        import traceback
        print("=== ERREUR DÉTAILLÉE ===")
        traceback.print_exc()
        messagebox.showerror("Erreur API", f"Une erreur est survenue : {e}")
    finally:
        gen_button.config(state=tk.NORMAL, text="Générer description et estimation")

# Gestion des photos
def ajouter_photos():
    fichiers = filedialog.askopenfilenames(filetypes=[("Images", "*.png *.jpg *.jpeg")])
    for f in fichiers:
        if f not in photo_paths:
            photo_paths.append(f)
            photo_listbox.insert(tk.END, os.path.basename(f))

def supprimer_photo():
    selections = photo_listbox.curselection()
    for index in reversed(selections):
        photo_paths.pop(index)
        photo_listbox.delete(index)

def copier_description():
    root.clipboard_clear()
    root.clipboard_append(description_text.get("1.0", tk.END))
    messagebox.showinfo("Copié", "Description copiée dans le presse-papiers.")

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

# Interface graphique
root = tk.Tk()
root.title("Vinted Estimate")
root.geometry("600x700")
root.configure(bg="#54acb4")  # Couleur de fond principale

# Icône
icon_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
icon_image = PhotoImage(file=icon_path)
root.iconphoto(True, icon_image)

# Style moderne avec ta palette
style = ttk.Style()
style.configure("TButton",
                font=("Helvetica", 12),
                padding=10,
                relief="flat",
                background="#75c4cc",
                foreground="white")
style.map("TButton",
          background=[("active", "#0c2c4c")],
          foreground=[("active", "white")])

# Titre
titre_label = tk.Label(root, text="Vinted Estimate", font=("Helvetica", 20, "bold"),
                       bg="#54acb4", fg="#0c2c4c")
titre_label.pack(pady=10)

# Liste des photos
photo_paths = []
photo_button = ttk.Button(root, text="Ajouter des photos", command=ajouter_photos)
photo_button.pack(pady=5)

photo_listbox = Listbox(root, selectmode=MULTIPLE, width=50, height=5,
                        bg="#f5eee6", fg="#0c2c4c", font=("Arial", 11), relief="flat", borderwidth=2)
photo_listbox.pack(pady=5)

delete_photo_button = ttk.Button(root, text="Supprimer la/les photo(s) sélectionnée(s)", command=supprimer_photo)
delete_photo_button.pack(pady=5)

# Générer
gen_button = ttk.Button(root, text="Générer description et estimation", command=generer_description)
gen_button.pack(pady=10)

# Zone de texte description
description_text = tk.Text(root, height=10, width=60, bg="#f5eee6", fg="#0c2c4c",
                           font=("Arial", 12), relief="flat", borderwidth=2)
description_text.pack(pady=5)

# Copier / Sauvegarder
copy_button = ttk.Button(root, text="Copier la description", command=copier_description)
copy_button.pack(pady=5)

save_button = ttk.Button(root, text="Sauvegarder dans un fichier", command=sauvegarder_description)
save_button.pack(pady=5)

root.mainloop()
