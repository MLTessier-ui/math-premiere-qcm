--- a/app.py
+++ b/app.py
@@
-from qcm_engine import THEMES, Difficulty, generate_set, generate_exam, to_dict, validate
+from qcm_engine import THEMES, Difficulty, generate_set, generate_exam, to_dict, validate
@@
-    theme = st.selectbox("Thème", options=["Auto"] + THEMES)
-    difficulty = st.selectbox("Difficulté", options=Difficulty, index=1)
-    n_questions = st.slider("Nombre de questions", 3, 30, 8)
-    exam_mode = st.toggle("Mode examen (12 questions, thèmes variés)")
-    use_llm = st.toggle("Reformulation LLM (optionnel)", value=False, help="Désactivé par défaut pour la vitesse/robustesse.")
+    theme = st.selectbox("Thème", options=["Auto"] + THEMES, help="Choisissez un thème officiel du BO ou 'Auto' pour tirage aléatoire.")
+    difficulty = st.selectbox("Difficulté", options=Difficulty, index=1, help="Facile, Moyen ou Difficile.")
+    n_questions = st.slider("Nombre de questions", 3, 30, 8, help="Nombre de questions pour l'entraînement.")
+    exam_mode = st.toggle("Mode examen (12 questions, couvrant tous les thèmes)")
+    use_llm = st.toggle("Reformulation LLM (optionnel)", value=False, help="Pour paraphraser l’énoncé/explication, sans toucher aux corrections.")
@@
-    if t == "affine":
+    if t == "affine":
         a, b = payload["a"], payload["b"]
         xs = np.linspace(-6, 6, 100)
         ys = a*xs + b
@@
-    elif t == "quadratique":
-        p, qv = payload["p"], payload["q"]
-        xs = np.linspace(p-6, p+6, 200)
-        ys = (xs - p)**2 + qv
-        plt.plot(xs, ys)
-        for x0, y0 in payload.get("points", []):
-            plt.scatter([x0], [y0])
-        plt.title(f"f(x) = (x - {p})² + {qv}")
-        st.pyplot(plt.gcf(), clear_figure=True)
-    elif t == "stats_hist":
+    elif t == "stats_hist":
         data = payload["data"]
         plt.hist(data, bins="auto")
-        plt.title("Histogramme des données")
+        plt.title("Histogramme de la série statistique")
         st.pyplot(plt.gcf(), clear_figure=True)
