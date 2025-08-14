# -*- coding: utf-8 -*-
import json
import random
import openai
import streamlit as st
import csv
from io import StringIO

# Configuration de la page
st.set_page_config(page_title="Chatbot QCM Maths", page_icon="🧮")
st.title("🤖 Chatbot QCM – Maths Première (enseignement spécifique)")

# Choix du chapitre
chapitres = [
    "Fonctions", "Dérivation", "Statistiques", "Suites",
    "Trigonométrie", "Probabilités", "Géométrie", "Nombres et calculs", "Grandeurs et mesures"
]
chapitre_choisi = st.selectbox("📘 Chapitre :", chapitres)

# Choix du nombre de questions
nb_questions = st.slider("Nombre de questions :", min_value=5, max_value=20, value=10)

# Choix du niveau de difficulté
niveaux = ["Facile", "Standard", "Difficile"]
niveau_choisi = st.selectbox("Niveau de difficulté :", niveaux)

# Mode examen (correction à la fin)
mode_examen = st.checkbox("Mode examen (correction à la fin)")

# Clé API
try:
    key = st.secrets["OPENAI_API_KEY"]
    key.encode("ascii")
except (KeyError, UnicodeEncodeError):
    st.error("❌ Clé API invalide ou manquante.")
    st.stop()

client = openai.OpenAI(api_key=key)

# Initialisation de session_state
if 'qcm_data' not in st.session_state:
    st.session_state.qcm_data = None
if 'answer_submitted' not in st.session_state:
    st.session_state.answer_submitted = False
if 'user_answer' not in st.session_state:
    st.session_state.user_answer = None
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'nb_questions' not in st.session_state:
    st.session_state.nb_questions = 0
if 'user_answers_list' not in st.session_state:
    st.session_state.user_answers_list = []
if 'max_questions' not in st.session_state:
    st.session_state.max_questions = nb_questions

# Synchronisation avec le slider
st.session_state.max_questions = nb_questions


def generate_unique_qcm(chapitre: str, niveau: str, tries: int = 3):
    for _ in range(tries):
        prompt = f"""
Tu es un professeur de mathématiques. Génère UNE question de QCM niveau Première.
- Chapitre : {chapitre}
- Difficulté : {niveau}
- Propose 4 réponses DIFFÉRENTES et plausibles.
- Indique UNE seule bonne réponse par sa lettre (A, B, C ou D).
- Donne une explication pédagogique concise.

Réponds STRICTEMENT en JSON (sans texte autour) :
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
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        content = resp.choices[0].message.content
        data = json.loads(content)

        original_options = {k.upper(): str(v).strip() for k, v in data["options"].items()}
        letters = ["A", "B", "C", "D"]
        original_items = [(L, original_options[L]) for L in letters if L in original_options]
        if len(original_items) != 4:
            continue

        sigs = [t.casefold().strip() for _, t in original_items]
        if len(set(sigs)) != 4:
            continue

        correct_old = str(data["correct_answer"]).strip().upper()
        if correct_old not in letters:
            continue

        items = original_items[:]
        random.shuffle(items)
        new_letters = ["A", "B", "C", "D"]
        mapping = list(zip(new_letters, items))
        shuffled_options = {newL: text for newL, (oldL, text) in mapping}
        correct_new = next((newL for newL, (oldL, _) in mapping if oldL == correct_old), None)
        if correct_new is None:
            continue

        return data["question"], shuffled_options, correct_new, data["explanation"]

    raise ValueError("Impossible d'obtenir un QCM valide après plusieurs tentatives.")


# Gestion des questions et réponses
if 'current_form_key' not in st.session_state:
    st.session_state.current_form_key = 0

while st.session_state.nb_questions < st.session_state.max_questions:
    form_key = f'qcm_form_{st.session_state.current_form_key}'
    with st.form(key=form_key):
        if st.session_state.qcm_data is None or st.session_state.answer_submitted:
            try:
                q, opts, corr, expl = generate_unique_qcm(chapitre_choisi, niveau_choisi, tries=4)
                st.session_state.qcm_data = {
                    'question': q,
                    'options': opts,
                    'correct_answer': corr,
                    'explanation': expl,
                }
                st.session_state.answer_submitted = False
                st.session_state.user_answer = None
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération du QCM : {e}")
                break

        q = st.session_state.qcm_data
        st.markdown(f"**❓ Question :** {q['question']}")
        st.session_state.user_answer = st.radio(
            "Choisis ta réponse :",
            ["A", "B", "C", "D"],
            format_func=lambda k: f"{k} : {q['options'][k]}"
        )

        if st.form_submit_button("✅ Valider ma réponse"):
            st.session_state.answer_submitted = True
            user_letter = st.session_state.user_answer

            st.session_state.user_answers_list.append({
                'question': q['question'],
                'selected': user_letter,
                'selected_text': q['options'][user_letter],
                'correct_letter': q['correct_answer'],
                'correct_text': q['options'][q['correct_answer']],
                'explanation': q['explanation']
            })

            if not mode_examen:
                if user_letter == q['correct_answer']:
                    st.success("✅ Bravo, c'est la bonne réponse !")
                    st.session_state.score += 1
                else:
                    st.error(f"❌ Mauvais choix. La bonne réponse était **{q['correct_answer']} : {q['options'][q['correct_answer']]}**")
                st.markdown(f"**💡 Explication :** {q['explanation']}")

            st.session_state.nb_questions += 1
            st.session_state.current_form_key += 1
            st.experimental_rerun()

# Affichage du score et progression
st.progress(0 if st.session_state.max_questions == 0 else st.session_state.nb_questions / st.session_state.max_questions)
st.markdown(f"### 🧮 Score : {st.session_state.score} / {st.session_state.nb_questions}")

# Fin du quiz et correction
if st.session_state.nb_questions >= st.session_state.max_questions:
    if mode_examen:
        st.success("🎉 Quiz terminé ! Correction finale :")
        final_score = 0
        for i, ans in enumerate(st.session_state.user_answers_list, 1):
            if ans['selected'] == ans['correct_letter']:
                final_score += 1
                result = '✅ Correct'
            else:
                result = f"❌ Incorrect (Bonne réponse : {ans['correct_letter']} : {ans['correct_text']})"
            st.markdown(
                f"**Q{i} :** {ans['question']}  \n"
                f"**Votre réponse :** {ans['selected']} : {ans['selected_text']}  \n"
                f"**Résultat :** {result}  \n"
                f"**Explication :** {ans['explanation']}"
            )
        st.success(f"🧮 Score final : {final_score} / {len(st.session_state.user_answers_list)}")
    else:
        st.success(f"🎉 Quiz terminé ! Tu as obtenu {st.session_state.score} / {st.session_state.max_questions} bonnes réponses.")

    # Export CSV
    if st.button("📥 Exporter les résultats CSV"):
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=['question', 'selected', 'selected_text', 'correct_letter', 'correct_text', 'explanation'])
        writer.writeheader()
        for ans in st.session_state.user_answers_list:
            writer.writerow(ans)
        st.download_button("Télécharger CSV", output.getvalue(), file_name="resultats_qcm.csv", mime="text/csv")

    if st.button("🔁 Recommencer un nouveau quiz"):
        st.session_state.score = 0
        st.session_state.nb_questions = 0
        st.session_state.qcm_data = None
        st.session_state.answer_submitted = False
        st.session_state.user_answers_list = []
        st.session_state.max_questions = nb_questions
        st.session_state.current_form_key = 0
        st.experimental_rerun()
