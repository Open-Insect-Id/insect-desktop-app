import customtkinter as ctk
from PIL import Image
import tkinter as tk
from tkinter import filedialog
import numpy as np
import random
from preprocess import preprocess_pil_image

# Apparence par défaut
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class InsectDetectorApp(ctk.CTk):
    def __init__(self, session, input_name, output_name, input_size, insect_species):
        super().__init__()

        # --- Modèle et métadonnées ---
        self.session = session
        self.input_name = input_name
        self.output_name = output_name
        self.input_size = input_size
        self.insect_species = insect_species or ["unknown"] * 1000

        # --- UI ---
        self.title("🦋 Open Insect Identifier")
        self.geometry("900x600")
        self.minsize(800, 500)

        # Etat
        self.image_path = None
        self.current_pil_image = None
        self.analyzing = False

        # Grille
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_widgets()
        # Afficher l'état du modèle
        status_text = self._status_message('model_loaded') if self.session is not None else self._status_message('model_missing')
        self.update_status(status_text)

    def create_widgets(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        self.lbl_logo = ctk.CTkLabel(self.sidebar, text="Open Insect Identifier", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_upload = ctk.CTkButton(self.sidebar, text="📁 Charger Image", command=self.upload_image)
        self.btn_upload.grid(row=1, column=0, padx=20, pady=10)

        self.btn_analyze = ctk.CTkButton(self.sidebar, text="🔍 Identifier", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.start_analysis)
        self.btn_analyze.grid(row=2, column=0, padx=20, pady=10)
        self.btn_analyze.configure(state="disabled")

        self.btn_clear = ctk.CTkButton(self.sidebar, text="Effacer", fg_color="#cf3838", hover_color="#9e2b2b", command=self.clear_interface)
        self.btn_clear.grid(row=3, column=0, padx=20, pady=10)

        self.lbl_status = ctk.CTkLabel(self.sidebar, text="Prêt", font=ctk.CTkFont(size=12))
        self.lbl_status.grid(row=5, column=0, padx=20, pady=20)

        # Main view
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_view.grid_rowconfigure(0, weight=3)
        self.main_view.grid_rowconfigure(1, weight=1)
        self.main_view.grid_columnconfigure(0, weight=1)

        self.image_frame = ctk.CTkFrame(self.main_view, fg_color=("gray90", "gray16"))
        self.image_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 20))

        self.lbl_image = ctk.CTkLabel(self.image_frame, text="Aucune image sélectionnée")
        self.lbl_image.place(relx=0.5, rely=0.5, anchor="center")

        self.result_frame = ctk.CTkTextbox(self.main_view, font=ctk.CTkFont(family="Courier", size=13))
        self.result_frame.grid(row=1, column=0, sticky="nsew")
        self.result_frame.insert("0.0", "Les résultats de l'analyse apparaîtront ici...")
        self.result_frame.configure(state="disabled")

    def _status_message(self, key):
        messages = {
            'model_loaded': [
                "Modèle chargé ✔ \nprêt à détecter des bestioles",
                "Modèle prêt \nque la chasse commence!",
                "Modèle chargé ✔ \nl'IA est éveillée (café consommé)"
            ],
            'model_missing': [
                "Je ne sais pas du tout comment tu as fait pour avoir cette erreur mais le modèle n'est pas chargé ❌",
                "Modèle absent - il a pris des vacances 🏖️",
                "Modèle introuvable - il joue à cache-cache 🫣"
            ],
            'image_loaded': [
                "Image chargée - belle prise!",
                "Image reçue 🖼️ - prépare les loupes",
                "Image chargée - prêts pour l'analyse!"
            ],
            'analysis_start': [
                "Analyse en cours… L'IA scrute la bestiole 🧐",
                "On analyse... mets-toi à l'aise, ça prend une coffee break ☕",
                "Analyse en cours - patience, la science travaille"
            ],
            'analysis_done': [
                "Analyse terminée ✔ - verdict ci-dessous",
                "Terminé ✅ - que la meilleure espèce gagne!",
                "Analyse finie - résultats prêts 🎉"
            ],
            'analysis_error': [
                "Oops - l'analyse a trébuché. L'IA va se faire une tasse de thé ☕",
                "Erreur durant l'analyse - réessaie ou vérifie l'image.",
                "L'algorithme a croisé un fil orange - redémarrage conseillé 😅"
            ],
            'no_model': [
                "Aucun modèle chargé. Impossible d'analyser (le modèle a fui).",
                "Pas de bras, pas de chocolat. Ah non, pas de modèle, pas d'analyse!",
            ],
            'ready': [
                "Prêt",
                "Prêt - prêt à chasser des insectes!",
                "Prêt (en mode veille, mais opérationnel)"
            ]
        }
        return random.choice(messages.get(key, [str(key)]))

    def update_status(self, text):
        self.lbl_status.configure(text=text)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if file_path:
            self.image_path = file_path
            self.display_image(file_path)
            self.btn_analyze.configure(state="normal")
            self.update_status(self._status_message('image_loaded'))

    def display_image(self, path):
        img = Image.open(path)

        frame_width = self.image_frame.winfo_width()
        frame_height = self.image_frame.winfo_height()
        if frame_width < 10:
            frame_width = 400
        if frame_height < 10:
            frame_height = 300

        # Calcul du ratio pour ne pas déformer
        ratio = min(frame_width/img.width, frame_height/img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))

        self.current_image_tk = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=new_size
        )

        self.lbl_image.configure(image=self.current_image_tk, text="")
        self.current_pil_image = img

    def clear_interface(self):
        self.lbl_image.configure(image=None, text="Aucune image sélectionnée")
        self.image_path = None
        self.btn_analyze.configure(state="disabled")
        self.write_result("En attente d'image...")
        self.update_status(self._status_message('ready'))

    def write_result(self, text):
        self.result_frame.configure(state="normal")
        self.result_frame.delete("0.0", "end")
        self.result_frame.insert("0.0", text)
        self.result_frame.configure(state="disabled")

    def start_analysis(self):
        if not self.image_path or self.analyzing:
            return
        if self.session is None:
            self.write_result(self._status_message('model_missing'))
            self.update_status(self._status_message('no_model'))
            return

        self.analyzing = True
        self.btn_analyze.configure(state="disabled")
        self.update_status(self._status_message('analysis_start'))

        # Lancer en tâche de fond pour garder l'UI réactive
        self.after(50, self._run_inference)



    # Aide IA pour la correction de la proba
    def _run_inference(self):
        try:
            # Prétraitement
            img_arr = preprocess_pil_image(self.current_pil_image, self.input_size)
            
            # Inférence (Récupération des Logits bruts)
            outputs = self.session.run([self.output_name], {self.input_name: img_arr})
            raw_logits = outputs[0][0] # Ce sont les scores bruts (ex: 4.35, -0.6...)
            
            # --- CORRECTION : APPLIQUER SOFTMAX ---
            # La formule magique pour transformer les scores en % (0 à 1)
            # On soustrait le max pour la stabilité numérique (éviter d'exploser avec np.exp)
            exp_vals = np.exp(raw_logits - np.max(raw_logits))
            predictions = exp_vals / exp_vals.sum()
            # --------------------------------------
            
            # On prend les 3 meilleurs
            top_indices = np.argsort(predictions)[::-1][:3]
            top_scores = predictions[top_indices]
            
            final_text = "🔎 RÉSULTATS DE L'ANALYSE\n" + "-"*30 + "\n\n"
            
            for i, (idx, score) in enumerate(zip(top_indices, top_scores)):
                conf = score * 100 # Maintenant score est entre 0 et 1, donc conf entre 0 et 100
                
                if idx < len(self.insect_species):
                    name = self.insect_species[idx]
                else:
                    name = f"Classe {idx} (Hors liste)"
                
                # Barre de progression (max 20 caractères)
                bar_len = int(conf / 5) 
                bar = "█" * bar_len + "░" * (20 - bar_len)
                
                final_text += f"#{i+1} {name}\n"
                final_text += f"   {conf:.1f}% {bar}\n\n"
            
            self.write_result(final_text)
            self.update_status(self._status_message('analysis_done'))
            
        except Exception as e:
            self.write_result(f"Erreur: {e}")
            self.update_status(self._status_message('analysis_error'))
            print(f"Erreur inférence: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.analyzing = False
            self.btn_analyze.configure(state="normal")
