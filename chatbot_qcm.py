# -*- coding: utf-8 -*-
import json
import random
import openai
import streamlit as st
import sys
import re
import pandas as pd
import os

# Configuration
st.set_page_config(page_title="Chatbot QCM Maths", page_icon="🧮")
st.title("🤖 Chatbot QCM – Maths Première (enseignement spécifique)")

# Thèmes + automatismes officiels
themes_automatismes = {
    "Calcul numérique et algébrique": "Règles de calcul, priorités, puissances, factorisations simples, développements simples, identités remarquables.",
    "Proportions et pourcentages": "Proportionnalité, échelles, pourcentages simples et successifs, variations relatives.",
    "Évolutions et variations": "Augmentations, diminutions, taux d’évolution, variations composées.",
    "Fonctions et représentations": "Lecture simple de tableaux ou d'expressions, valeurs, variations.",
    "Statistiques": "Tableaux, moyennes, médianes, étendues, calculs simples.",
    "Probabilités": "Expériences aléatoires simples, calculs de probabilités, événements contraires."
}

# --- Interface utilisateur ---
nb_questions = st.slider("Nombre de questions", 5, 20, 10)
chapitres = list(themes_automatismes.keys())
chapitre_choisi = st.selectbox("📘 Chapitre :", ["--- Choisir un chapitre ---"] + chapitres)
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
    "answers_log": [],
    "explication_lue": False,
    "last_feedback": None
}.items():
    if var not in st.session_state:
        st.session_state[var] = default

st.session_state.max_questions = nb_questions

# Génération QCM
def generate_unique_qcm():
    description_theme = themes_automatismes[chapitre_choisi]
    prompt_data = f"""Tu es un professeur de mathématiques.
Génère une question QCM niveau Première (enseignement spécifique) sur le thème suivant : {chapitre_choisi}.
Les questions doivent respecter les automatismes suivants : {description_theme}.
La difficulté est : {difficulte}.

⚠️ Contraintes importantes :
- La question doit être autonome, claire et compréhensible SANS graphique, tableau ou schéma externe.
- Elle doit pouvoir être résolue en CALCUL MENTAL ou avec des calculs très simples.
- Les nombres utilisés doivent être SIMPLES : inférieurs à 100, maximum 2 chiffres.
- Les calculs doivent pouvoir être faits de tête en moins de 30 secondes.
- Fournis exactement 4 réponses différentes : A, B, C, D.
- Une SEULE réponse doit être correcte et ABSOLUMENT incluse dans les options.
- Les 3 autres doivent être fausses mais plausibles.
- L'explication doit justifier pourquoi la bonne réponse est correcte et pourquoi les autres sont fausses.

Réponds STRICTEMENT en JSON valide avec guillemets doubles :
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
            model="gpt-4o-mini",
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

        # Vérification unicité
        if qcm_raw["question"] in st.session_state.seen_questions:
            return None
        st.session_state.seen_questions.add(qcm_raw["question"])

        # Mélange options
        original_options = qcm_raw["options"]
        correct_text = original_options[qcm_raw["correct_answer"]]
        items = list(original_options.items())
        random.shuffle(items)
        new_letters = ["A", "B", "C", "D"]
        shuffled_options = {new_letter: text for new_letter, (_, text) in zip(new_letters, items)}
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
        for _ in range(3):  # max 3 essais
            qcm = generate_unique_qcm()
            if qcm:
                st.session_state.qcm_data = qcm
                break

# Affichage QCM
if chapitre_choisi != "--- Choisir un chapitre ---" and st.session_state.qcm_data and st.session_state.nb_questions < st.session_state.max_questions:
    q = st.session_state.qcm_data

    st.markdown(f"**❓ Question {st.session_state.nb_questions+1}/{st.session_state.max_questions} :** {q['question']}")

    # Étape 1 : réponse
    if not st.session_state.explication_lue:
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

            feedback = ""
            if not mode_examen:
                if is_correct:
                    feedback = "✅ Bravo, c'est la bonne réponse !"
                    st.success(feedback)
                else:
                    feedback = f"❌ Mauvais choix. La bonne réponse était **{correct_letter} : {q['options'][correct_letter]}**"
                    st.error(feedback)
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

            st.session_state.explication_lue = True
            st.session_state.last_feedback = feedback

    # Étape 2 : confirmation lecture explication
    else:
        if st.session_state.last_feedback:
            st.info(st.session_state.last_feedback)
            st.markdown(f"<span style='color:black;'><b>💡 Explication :</b> {q['explanation']}</span>", unsafe_allow_html=True)

        if st.button("👉 J’ai lu l’explication, question suivante"):
            st.session_state.nb_questions += 1
            st.session_state.qcm_data = None
            st.session_state.explication_lue = False
            st.session_state.last_feedback = None
            st.rerun()

# Fin du quiz
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
        st.download_button("📥 Télécharger l'historique", df_hist.to_csv(index=False), "resultats_qcm.csv")

    if st.button("🔁 Recommencer un nouveau quiz"):
        st.session_state.score = 0
        st.session_state.nb_questions = 0
        st.session_state.qcm_data = None
        st.session_state.answers_log.clear()
        st.session_state.seen_questions.clear()
        st.session_state.explication_lue = False
        st.session_state.last_feedback = None
        st.rerun()
