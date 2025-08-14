# -*- coding: utf-8 -*-
import json
import random
import openai
import streamlit as st
import sys
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

# Formulaire pour gérer les questions et réponses
with st.form(key='qcm_form'):
    if st.session_state.qcm_data is None or st.session_state.answer_submitted:
        if st.form_submit_button("🎲 Nouvelle question") and st.session_state.nb_questions < st.session_state.max_questions:
            st.session_state.answer_submitted = False
            st.session_state.user_answer = None

            prompt_data = {
                "instructions": f"""Tu es un professeur de mathématiques. Génère une question QCM niveau Première.
- Chapitre : {chapitre_choisi}
- Difficulté : {niveau_choisi}
- Fournis UNE question claire.
- Propose 4 réponses DIFFÉRENTES.
- Donne UNE seule bonne réponse (ex: 'B').
- Donne une explication pédagogique.
- Ne commence pas par 'Voici une question...'.
Réponds en JSON comme ceci : {{
  'question': '...',
  'options': {{'A': '...', 'B': '...', 'C': '...', 'D': '...'}},
  'correct_answer': 'B',
  'explanation': '...'
}}"""
            }

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt_data["instructions"]}],
                    temperature=0.7
                )
                qcm_raw = json.loads(response.choices[0].message.content)

                # Mélange des options
                original_options = qcm_raw['options']
                correct_text = original_options[qcm_raw['correct_answer']]
                items = list(original_options.items())
                random.shuffle(items)
                letters = ["A", "B", "C", "D"]
                shuffled_options = {new_letter: text for new_letter, (_, text) in zip(letters, items)}

                # Recalcul de la bonne lettre
                for new_letter, text in shuffled_options.items():
                    if text == correct_text:
                        correct_letter = new_letter
                        break

                st.session_state.qcm_data = {
                    'question': qcm_raw['question'],
                    'options': shuffled_options,
                    'correct_answer': correct_letter,
                    'explanation': qcm_raw['explanation']
                }

            except Exception as e:
                st.error(f"❌ Erreur GPT : {e}")
                st.session_state.qcm_data = None

    if st.session_state.qcm_data:
        q = st.session_state.qcm_data
        st.markdown(f"**❓ Question :** {q['question']}")
        st.session_state.user_answer = st.radio(
            "Choisis ta réponse :",
            list(q['options'].keys()),
            format_func=lambda k: f"{k} : {q['options'][k]}"
        )

        if st.form_submit_button("✅ Valider ma réponse") and not st.session_state.answer_submitted:
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

# Score et progression
st.markdown(f"### 🧮 Score : {st.session_state.score} / {st.session_state.nb_questions}")

# Fin du quiz et correction
if st.session_state.nb_questions >= st.session_state.max_questions or (st.session_state.nb_questions == st.session_state.max_questions-1 and mode_examen and st.session_state.qcm_data):
    if mode_examen:
        st.success("🎉 Quiz terminé ! Correction finale :")
        final_score = 0
        for i, ans in enumerate(st.session_state.user_answers_list, 1):
            if ans['selected'] == ans['correct_letter']:
                final_score += 1
                result = '✅ Correct'
            else:
                result = f"❌ Incorrect (Bonne réponse : {ans['correct_letter']} : {ans['correct_text']})"
            st.markdown(f"**Q{i} :** {ans['question']}  \n**Votre réponse :** {ans['selected']} : {ans['selected_text']}  \n**Résultat :** {result}  \n**Explication :** {ans['explanation']}")
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
