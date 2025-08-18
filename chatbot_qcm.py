# -*- coding: utf-8 -*-
import json
import random
import openai
import streamlit as st
import re
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

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
    "Fonctions et représentations": "Lecture simple de tableaux ou d'expressions, valeurs, variations, pente, lecture graphique.",
    "Statistiques": "Tableaux, moyennes, médianes, étendues, calculs simples.",
    "Probabilités": "Expériences aléatoires simples, calculs de probabilités, événements contraires."
}

# ------------------------------
# Interface utilisateur
# ------------------------------
nb_questions = st.slider("Nombre de questions", 5, 20, 10)
chapitres = list(themes_automatismes.keys())
chapitre_choisi = st.selectbox("📘 Chapitre :", ["--- Choisir un chapitre ---"] + chapitres)
difficulte = st.selectbox("Niveau de difficulté", ["Facile", "Moyen", "Difficile"])
mode_examen = st.checkbox("Mode examen (corrigé à la fin)")
show_graphics = st.checkbox("🖼️ Générer les graphiques quand c’est possible")

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
# États
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
    "last_explanation": None,
    "nb_graphics": 0  # compteur pour quota graphique
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v
st.session_state.max_questions = nb_questions

# ------------------------------
# Fonctions utilitaires
# ------------------------------
def plot_from_support(support_type, support_md):
    try:
        if support_type == "table":
            lines = [l.strip("| ") for l in support_md.strip().splitlines() if "|" in l]
            if len(lines) >= 2:
                values = [l.split("|") for l in lines[2:]]
                xs, ys = [], []
                for v in values:
                    try:
                        xs.append(float(v[0].strip()))
                        ys.append(float(v[1].strip()))
                    except:
                        pass
                if xs and ys:
                    fig, ax = plt.subplots()
                    ax.plot(xs, ys, marker="o")
                    ax.set_title("Lecture graphique (tableau)")
                    st.pyplot(fig)
                    return True
        elif support_type == "description":
            match = re.search(r"f\(x\)\s*=\s*([0-9x\+\-\*/\s^]+)", support_md)
            if match:
                expr = match.group(1).replace("^", "**")
                f = lambda x: eval(expr, {"x": x, "np": np})
                xs = np.linspace(-5, 5, 200)
                ys = [f(x) for x in xs]
                fig, ax = plt.subplots()
                ax.plot(xs, ys, label=f"f(x)={expr}")
                ax.axhline(0, color="black", linewidth=0.5)
                ax.axvline(0, color="black", linewidth=0.5)
                ax.legend()
                ax.set_title("Courbe de la fonction")
                st.pyplot(fig)
                return True
    except Exception:
        return False
    return False

# ------------------------------
# Génération QCM
# ------------------------------
def generate_unique_qcm():
    description_theme = themes_automatismes[chapitre_choisi]
    difficulte_guidelines = {
        "Facile": "Automatisme direct, calcul mental < 10 s, nombres simples ≤ 100.",
        "Moyen": "Au moins une étape de raisonnement intermédiaire (comparaison, pente, propriété).",
        "Difficile": "Plusieurs étapes logiques ou combinaison de notions, faisable sans calculatrice."
    }

    need_graphic = False
    if chapitre_choisi == "Fonctions et représentations":
        min_graphics = int(0.3 * st.session_state.max_questions)
        if st.session_state.nb_graphics < min_graphics:
            need_graphic = True

    prompt_data = f"""Tu es un professeur de mathématiques.
Génère UNE question QCM niveau Première (enseignement spécifique) sur le thème : {chapitre_choisi}.
Automatismes : {description_theme}.
Niveau : {difficulte} → {difficulte_guidelines[difficulte]}.

⚠️ Contraintes :
- EXACTEMENT 4 options différentes.
- UNE SEULE bonne réponse, incluse dans les options.
- Explication pédagogique brève.
- Ne cite pas A/B/C/D dans l'explication.
- La question doit être différente des précédentes (varie le type de tâche).
- { "La question DOIT inclure un support graphique (support_type = 'table' ou 'description')." if need_graphic else "Le support graphique est optionnel (none/table/description)." }

Réponds uniquement en JSON :
{{
  "question": "...",
  "support_type": "...",
  "support_md": "...",
  "options": {{
    "A": "...",
    "B": "...",
    "C": "...",
    "D": "..."
  }},
  "correct_answer": "B",
  "correct_answer_text": "...",
  "explanation": "..."
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_data}],
            temperature=0.5
        )
        content = response.choices[0].message.content.strip()
        qcm_raw = json.loads(re.search(r"\{.*\}", content, re.S).group())

        # Vérifications
        options = qcm_raw["options"]
        opt_texts = list(options.values())
        if len(set(opt_texts)) != 4:
            return None
        ca_text = qcm_raw["correct_answer_text"]
        if ca_text not in opt_texts:
            return None

        # Shuffle
        items = list(options.items())
        random.shuffle(items)
        shuffled_options = {L: t for L, (_, t) in zip(["A","B","C","D"], items)}
        correct_letter = next(L for L,t in shuffled_options.items() if t == ca_text)

        # Unicité
        if qcm_raw["question"] in st.session_state.seen_questions:
            return None
        st.session_state.seen_questions.add(qcm_raw["question"])

        # Compteur graphique
        if qcm_raw["support_type"] != "none":
            st.session_state.nb_graphics += 1

        return {
            "question": qcm_raw["question"],
            "support_type": qcm_raw["support_type"],
            "support_md": qcm_raw["support_md"],
            "options": shuffled_options,
            "correct_answer": correct_letter,
            "correct_answer_text": ca_text,
            "explanation": qcm_raw["explanation"]
        }
    except Exception:
        return None

# ------------------------------
# Boucle principale
# ------------------------------
if chapitre_choisi != "--- Choisir un chapitre ---":
    if (not st.session_state.qcm_data) and (st.session_state.nb_questions < st.session_state.max_questions):
        for _ in range(6):
            qcm = generate_unique_qcm()
            if qcm:
                st.session_state.qcm_data = qcm
                break

if (
    chapitre_choisi != "--- Choisir un chapitre ---"
    and st.session_state.qcm_data
    and st.session_state.nb_questions < st.session_state.max_questions
):
    q = st.session_state.qcm_data
    st.markdown(f"**❓ Question {st.session_state.nb_questions+1}/{st.session_state.max_questions} :** {q['question']}")

    # Support
    if q["support_type"] != "none" and q["support_md"]:
        st.markdown(q["support_md"])
        if show_graphics:
            plot_from_support(q["support_type"], q["support_md"])

    if not st.session_state.explication_lue:
        st.session_state.user_answer = st.radio(
            "Choisis ta réponse :", list(q["options"].keys()),
            format_func=lambda k: f"{k} : {q['options'][k]}", index=None
        )
        if st.button("✅ Valider ma réponse") and st.session_state.user_answer:
            user = st.session_state.user_answer
            correct = q["correct_answer"]
            is_correct = (user == correct)

            if not mode_examen:
                st.session_state.last_feedback = "✅ Bravo !" if is_correct else f"❌ Mauvais choix. Bonne réponse : {correct} : {q['options'][correct]}"
                st.session_state.last_explanation = q["explanation"]
                st.session_state.explication_lue = True
                if is_correct:
                    st.session_state.score += 1
                st.session_state.answers_log.append({
                    "question": q["question"],
                    "réponse élève": f"{user} : {q['options'][user]}",
                    "bonne réponse": f"{correct} : {q['options'][correct]}",
                    "explication": q["explanation"],
                    "correct": is_correct
                })
                st.rerun()
            else:
                st.session_state.nb_questions += 1
                st.session_state.qcm_data = None
                st.rerun()
    else:
        if st.session_state.last_feedback.startswith("✅"):
            st.success(st.session_state.last_feedback)
        else:
            st.error(st.session_state.last_feedback)
        st.markdown(f"💡 {st.session_state.last_explanation}")
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
    st.success(f"🎉 Terminé ! Score : {st.session_state.score}/{st.session_state.max_questions}")

    # Export CSV
    df = pd.DataFrame(st.session_state.answers_log)
    csv_path = "resultats_quiz.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")
    st.download_button("📥 Télécharger mes résultats (CSV)", data=df.to_csv(index=False).encode("utf-8"), file_name=csv_path)

    if st.button("🔁 Recommencer"):
        for k in defaults.keys():
            st.session_state[k] = defaults[k]
        st.rerun()
