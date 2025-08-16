# -*- coding: utf-8 -*-
import json
import random
import openai
import streamlit as st
import sys
import re
import pandas as pd
import os
import matplotlib.pyplot as plt

# Configuration
st.set_page_config(page_title="Chatbot QCM Maths", page_icon="🧮")
st.title("🤖 Chatbot QCM – Maths Première (enseignement spécifique)")

# Thèmes + automatismes officiels
themes_automatismes = {
    "Calcul numérique et algébrique": "Règles de calcul, priorités, puissances, factorisations simples, développements simples, identités remarquables.",
    "Proportions et pourcentages": "Proportionnalité, échelles, pourcentages simples et successifs, variations relatives.",
    "Évolutions et variations": "Augmentations, diminutions, taux d’évolution, variations composées.",
    "Fonctions et représentations": "Lecture graphique, valeurs, antécédents, variations, extrema.",
    "Statistiques": "Tableaux, diagrammes, moyennes, médianes, étendues.",
    "Probabilités": "Expériences aléatoires simples, calculs de probabilités, événements contraires."
}

# Sélection utilisateur
chapitres = list(themes_automatismes.keys())
chapitre_choisi = st.selectbox("📘 Chapitre :", ["--- Choisir un chapitre ---"] + chapitres)
nb_questions = st.slider("Nombre de questions", 5, 20, 10)
difficulte = st.selectbox("Niveau de difficulté", ["Facile", "Moyen", "Difficile"])
mode_examen = st.checkbox("Mode examen (corrigé à la fin)")

# Clé API
try:
    key = st.secrets["OPENAI_API_KEY"]
    key.encode("ascii")
except (KeyError, UnicodeEncodeError):
    st.error("❌ Clé API invalide ou manquante.")
    st.stop()

client = openai.OpenAI(api_key=key)

# Init session
for var, default in {
    "qcm_data": None,
    "user_answer": None,
    "score": 0,
    "nb_questions": 0,
    "max_questions": nb_questions,
    "seen_questions": set(),
    "answers_log": []
}.items():
    if var not in st.session_state:
        st.session_state[var] = default

st.session_state.max_questions = nb_questions

# Génération avec vérification optimisée
def generate_unique_qcm():
    description_theme = themes_automatismes[chapitre_choisi]
    prompt_data = f"""Tu es un professeur de mathématiques.
Génère une question QCM niveau Première (enseignement spécifique) sur le thème suivant : {chapitre_choisi}.
Les questions doivent respecter les automatismes suivants : {description_theme}
Difficulté : {difficulte}.

- Fournis UNE question claire et concise.
- Propose 4 réponses DIFFÉRENTES.
- Donne UNE seule bonne réponse (ex: 'B').
- Donne une explication pédagogique courte.
- Réponds STRICTEMENT en JSON valide avec guillemets doubles pour clés et valeurs.
{{
  "question": "...",
  "options": {{
    "A": "...",
    "B": "...",
    "C": "...",
    "D": "..."
  }},
  "correct_answer": "B",
  "explanation": "..."
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",   # 🚀 modèle rapide
            messages=[{"role": "user", "content": prompt_data}],
            temperature=0.5
        )
        content = response.choices[0].message.content.strip()
        try:
            qcm_raw = json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.S)
            if match:
                qcm_raw = json.loads(match.group())
            else:
                return None

        if qcm_raw["question"] in st.session_state.seen_questions:
            return None

        # (filtrage désactivé pour ne pas bloquer les questions)
        st.session_state.seen_questions.add(qcm_raw["question"])

        # Mélange options
        original_options = qcm_raw["options"]
        items = list(original_options.items())
        random.shuffle(items)
        new_letters = ["A", "B", "C", "D"]
        shuffled_options = {new_letter: text for new_letter, (_, text) in zip(new_letters, items)}

        correct_text = original_options[qcm_raw["correct_answer"]]
        correct_letter = next(letter for letter, text in shuffled_options.items() if text == correct_text)

        return {
            "question": qcm_raw["question"],
            "options": shuffled_options,
            "correct_answer": correct_letter,
            "explanation": qcm_raw["explanation"]
        }
    except Exception:
        return None

# Sauvegarde CSV
def save_results_to_csv():
    filename = "resultats_qcm.csv"
    new_data = {
        "Chapitre": chapitre_choisi,
        "Difficulté": difficulte,
        "Score": st.session_state.score,
        "Questions_totales": st.session_state.max_questions
    }
    df_new = pd.DataFrame([new_data])
    if os.path.exists(filename):
        df_old = pd.read_csv(filename)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new
    df_all.to_csv(filename, index=False)

# Génération uniquement si un chapitre est choisi
if chapitre_choisi != "--- Choisir un chapitre ---":
    if (not st.session_state.qcm_data) and (st.session_state.nb_questions < st.session_state.max_questions):
        for _ in range(2):  # ⚡ max 2 essais seulement
            qcm = generate_unique_qcm()
            if qcm:
                st.session_state.qcm_data = qcm
                break

# Affichage QCM
if chapitre_choisi != "--- Choisir un chapitre ---" and st.session_state.qcm_data and st.session_state.nb_questions < st.session_state.max_questions:
    q = st.session_state.qcm_data
    st.markdown(f"**❓ Question {st.session_state.nb_questions+1}/{st.session_state.max_questions} :** {q['question']}")
    st.markdown(f"📌 Il reste {st.session_state.max_questions - st.session_state.nb_questions} questions")

    st.session_state.user_answer = st.radio(
        "Choisis ta réponse :",
        list(q["options"].keys()),
        format_func=lambda k: f"{k} : {q['options'][k]}",
        index=None
    )

    if st.button("✅ Valider ma réponse") and st.session_state.user_answer:
        user_letter = st.session_state.user_answer
        correct_letter = q["correct_answer"]
        is_correct = user_letter == correct_letter

        if not mode_examen:
            if is_correct:
                st.success("✅ Bravo, c'est la bonne réponse !")
            else:
                st.error(f"❌ Mauvais choix. La bonne réponse était **{correct_letter} : {q['options'][correct_letter]}**")
            st.markdown(f"<span style='color:black;'><b>💡 Explication :</b> {q['explanation']}</span>", unsafe_allow_html=True)

        st.session_state.answers_log.append({
            "question": q["question"],
            "votre réponse": f"{user_letter} : {q['options'][user_letter]}",
            "bonne réponse": f"{correct_letter} : {q['options'][correct_letter]}",
            "explication": q["explanation"],
            "correct": is_correct
        })

        if is_correct:
            st.session_state.score += 1
        st.session_state.nb_questions += 1
        st.session_state.qcm_data = None
        st.rerun()

# Fin
if chapitre_choisi != "--- Choisir un chapitre ---" and st.session_state.nb_questions >= st.session_state.max_questions:
    save_results_to_csv()
    st.success(f"🎉 Quiz terminé ! Tu as obtenu {st.session_state.score} / {st.session_state.max_questions} bonnes réponses.")

    if mode_examen:
        st.markdown("## 📄 Corrigé complet")
        for i, rep in enumerate(st.session_state.answers_log, 1):
            st.markdown(f"**Q{i} :** {rep['question']}")
            st.markdown(f"Votre réponse : {rep['votre réponse']}")
            st.markdown(f"Bonne réponse : {rep['bonne réponse']}")
            st.markdown(f"<span style='color:black;'>💡 {rep['explication']}</span>", unsafe_allow_html=True)
            st.markdown("---")

    if os.path.exists("resultats_qcm.csv"):
        st.markdown("## 📊 Historique des résultats")
        df_hist = pd.read_csv("resultats_qcm.csv")
        st.dataframe(df_hist)

        # Graphique global
        fig, ax = plt.subplots()
        ax.plot(range(1, len(df_hist) + 1), df_hist["Score"], marker="o", label="Score")
        ax.set_xlabel("Tentative")
        ax.set_ylabel("Score")
        ax.set_title("Évolution des scores")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

        # Graphique par chapitre colorisé avec % au-dessus
        st.markdown("### 📈 Score moyen par chapitre")
        moyennes = df_hist.groupby("Chapitre")["Score"].mean()

        couleurs = []
        for score in moyennes.values:
            if score >= 0.8 * nb_questions:
                couleurs.append("green")
            elif score >= 0.5 * nb_questions:
                couleurs.append("gold")
            else:
                couleurs.append("red")

        fig2, ax2 = plt.subplots()
        bars = ax2.bar(moyennes.index, moyennes.values, color=couleurs)
        ax2.set_ylabel("Score moyen")
        ax2.set_title("Score moyen par chapitre")
        plt.xticks(rotation=45, ha="right")

        # Ajout des pourcentages
        for bar, score in zip(bars, moyennes.values):
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                f"{(score/nb_questions)*100:.1f}%",
                ha="center", va="bottom", fontsize=9, fontweight="bold"
            )

        st.pyplot(fig2)

        st.download_button("📥 Télécharger l'historique", df_hist.to_csv(index=False), "resultats_qcm.csv")

    if st.button("🔁 Recommencer un nouveau quiz"):
        st.session_state.score = 0
        st.session_state.nb_questions = 0
        st.session_state.qcm_data = None
        st.session_state.answers_log.clear()
        st.session_state.seen_questions.clear()
        st.rerun()
