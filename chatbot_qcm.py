# -*- coding: utf-8 -*-
import json
import random
import openai
import streamlit as st
import sys
import re
import pandas as pd
import os

# ------------------------------
# Configuration
# ------------------------------
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

# ------------------------------
# Interface utilisateur (ordre souhaité)
# ------------------------------
nb_questions = st.slider("Nombre de questions", 5, 20, 10)
chapitres = list(themes_automatismes.keys())
chapitre_choisi = st.selectbox("📘 Chapitre :", ["--- Choisir un chapitre ---"] + chapitres)
difficulte = st.selectbox("Niveau de difficulté", ["Facile", "Moyen", "Difficile"])
mode_examen = st.checkbox("Mode examen (corrigé à la fin)")

# ------------------------------
# Clé API
# ------------------------------
try:
    key = st.secrets["OPENAI_API_KEY"]
    key.encode("ascii")
except (KeyError, UnicodeEncodeError):
    st.error("❌ Clé API invalide ou manquante.")
    st.stop()

client = openai.OpenAI(api_key=key)

# ------------------------------
# État de session
# ------------------------------
defaults = {
    "qcm_data": None,
    "user_answer": None,
    "score": 0,
    "nb_questions": 0,
    "max_questions": nb_questions,
    "seen_questions": set(),
    "answers_log": [],
    "explication_lue": False,
    "last_feedback": None,
    "last_explanation": None
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v
st.session_state.max_questions = nb_questions

# ------------------------------
# Outil : remapper les lettres citées dans l'explication après mélange
# ------------------------------
def remap_explanation_letters(expl: str, mapping_old_to_new: dict) -> str:
    """Remplace dans l'explication les références lettrelles (A/B/C/D) vers leur nouvelle lettre.
       Essaie de couvrir les formes: 'réponse A', 'option B', 'choix C', '(D)', 'D)'."""
    if not expl:
        return expl
    for old, new in mapping_old_to_new.items():
        # (réponse|option|choix) + lettre
        expl = re.sub(rf'(?i)\b(réponse|reponse|option|choix)\s*{old}\b',
                      lambda m: m.group(0)[:-1] + new, expl, flags=re.IGNORECASE)
        # (A) -> (NOUVELLE)
        expl = re.sub(rf'\(\s*{old}\s*\)', f'({new})', expl, flags=re.IGNORECASE)
        # A) -> NEW)
        expl = re.sub(rf'\b{old}\)', f'{new})', expl, flags=re.IGNORECASE)
        # "Réponse : A" -> "Réponse : NEW"
        expl = re.sub(rf'(?i)(réponse|reponse)\s*:\s*{old}\b',
                      lambda m: m.group(0)[:-1] + new, expl, flags=re.IGNORECASE)
    return expl

# ------------------------------
# Génération QCM
# ------------------------------
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
- Dans l'explication, N'UTILISE PAS les lettres A/B/C/D pour désigner les options ; explique le raisonnement et le résultat, sans citer de lettre.

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

        # Récup JSON robustement
        try:
            qcm_raw = json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.S)
            if not match:
                return None
            qcm_raw = json.loads(match.group())

        # Vérifs de cohérence
        if not isinstance(qcm_raw.get("options"), dict):
            return None
        # 4 options distinctes
        opt_texts = list(qcm_raw["options"].values())
        if len(opt_texts) != 4 or len(set(opt_texts)) != 4:
            return None
        # Bonne réponse présente
        if qcm_raw.get("correct_answer") not in qcm_raw["options"]:
            return None
        # Question non déjà vue
        if qcm_raw["question"] in st.session_state.seen_questions:
            return None

        # Mélange options + mapping ancien->nouveau
        original_options = qcm_raw["options"]
        items = list(original_options.items())  # [(old_letter, text), ...]
        random.shuffle(items)
        new_letters = ["A", "B", "C", "D"]
        shuffled_options = {new_letter: text for new_letter, (_, text) in zip(new_letters, items)}

        # mapping old -> new
        old_to_new = {}
        for new_letter, (_, text) in zip(new_letters, items):
            # retrouver l'ancienne lettre via le texte
            for old_letter, old_text in original_options.items():
                if old_text == text:
                    old_to_new[old_letter] = new_letter
                    break

        # lettre correcte après mélange
        correct_text = original_options[qcm_raw["correct_answer"]]
        correct_letter = next((L for L, t in shuffled_options.items() if t == correct_text), None)
        if correct_letter is None:
            return None

        # Remap des lettres éventuellement citées dans l'explication
        explanation = qcm_raw.get("explanation", "")
        explanation = remap_explanation_letters(explanation, old_to_new)

        st.session_state.seen_questions.add(qcm_raw["question"])

        return {
            "question": qcm_raw["question"],
            "options": shuffled_options,
            "correct_answer": correct_letter,
            "explanation": explanation
        }
    except Exception:
        return None

# ------------------------------
# Sauvegarde CSV (historique)
# ------------------------------
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

# ------------------------------
# Génération uniquement si un chapitre est choisi
# ------------------------------
if chapitre_choisi != "--- Choisir un chapitre ---":
    if (not st.session_state.qcm_data) and (st.session_state.nb_questions < st.session_state.max_questions):
        for _ in range(4):  # quelques essais en cas de JSON invalide
            qcm = generate_unique_qcm()
            if qcm:
                st.session_state.qcm_data = qcm
                break

# ------------------------------
# Affichage QCM
# ------------------------------
if chapitre_choisi != "--- Choisir un chapitre ---" and st.session_state.qcm_data and st.session_state.nb_questions < st.session_state.max_questions:
    q = st.session_state.qcm_data
    st.markdown(f"**❓ Question {st.session_state.nb_questions+1}/{st.session_state.max_questions} :** {q['question']}")

    # Étape 1 : choix + validation
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
            is_correct = (user_letter == correct_letter)

            # En mode entraînement : on montre tout de suite
            if not mode_examen:
                if is_correct:
                    st.session_state.last_feedback = "✅ Bravo, c'est la bonne réponse !"
                else:
                    st.session_state.last_feedback = f"❌ Mauvais choix. La bonne réponse était **{correct_letter} : {q['options'][correct_letter]}**"
                st.session_state.last_explanation = q["explanation"]

                # On bascule en mode "lecture explication"
                st.session_state.explication_lue = True

                # Log réponse
                st.session_state.answers_log.append({
                    "question": q["question"],
                    "votre réponse": f"{user_letter} : {q['options'][user_letter]}",
                    "bonne réponse": f"{correct_letter} : {q['options'][correct_letter]}",
                    "explication": q["explanation"],
                    "correct": is_correct
                })
                if is_correct:
                    st.session_state.score += 1

                # Re-rendu immédiat pour faire apparaître le bouton "J'ai lu..."
                st.rerun()

            # En mode examen : on enchaîne directement sans explication intermédiaire
            else:
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

    # Étape 2 : lecture + bouton pour continuer
    else:
        if st.session_state.last_feedback:
            # Affiche le feedback + l'explication
            if st.session_state.last_feedback.startswith("✅"):
                st.success(st.session_state.last_feedback)
            else:
                st.error(st.session_state.last_feedback)
            st.markdown(f"<span style='color:black;'><b>💡 Explication :</b> {st.session_state.last_explanation}</span>", unsafe_allow_html=True)

        if st.button("👉 J’ai lu l’explication, question suivante"):
            st.session_state.nb_questions += 1
            st.session_state.qcm_data = None
            st.session_state.explication_lue = False
            st.session_state.last_feedback = None
            st.session_state.last_explanation = None
            st.rerun()

# ------------------------------
# Fin du quiz
# ------------------------------
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
        st.session_state.last_explanation = None
        st.rerun()
