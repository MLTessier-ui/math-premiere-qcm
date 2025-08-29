--- a/qcm_engine.py
+++ b/qcm_engine.py
@@
-THEMES = [
-    "Fonctions", "Suites", "Statistiques & Probabilités",
-    "Géométrie analytique", "Calcul numérique", "Équations/Ineq."
-]
+THEMES = [
+    "Calcul numérique et algébrique",
+    "Proportions et pourcentages",
+    "Évolutions et variations",
+    "Fonctions et représentations",
+    "Statistiques",
+    "Probabilités"
+]
@@
-# -----------------------
-# GÉNÉRATEURS PAR THÈME
-# -----------------------
-def _gen_fonctions(difficulty: str, rng: random.Random) -> Question:
-    # Fonctions affines / quadratiques simples
-    ...
+#############################
+# GÉNÉRATEURS PAR THÈME (BO)
+#############################
+
+def _gen_calc_num(difficulty: str, rng: random.Random) -> Question:
+    # Exemple : puissances et fractions
+    a = rng.randint(2,5)
+    b = rng.randint(2,4)
+    stem = f"Calculer : ({a}²) × ({b}²)."
+    correct = str((a**2)*(b**2))
+    distractors = [str((a*b)**2), str(a**2 + b**2), str((a+b)**2)]
+    choices = [correct]+distractors
+    rng.shuffle(choices)
+    expl = f"({a}²)×({b}²) = ({a*a})×({b*b}) = {int(correct)}."
+    return Question("Calcul numérique et algébrique", difficulty, stem, choices, choices.index(correct), expl)
+
+
+def _gen_proportions(difficulty: str, rng: random.Random) -> Question:
+    total = rng.randint(80,150)
+    part = rng.randint(20,60)
+    stem = f"Dans une classe de {total} élèves, {part} sont des filles. Quelle proportion cela représente-t-il ?"
+    correct = f"{round(100*part/total,1)} %"
+    distractors = [f"{round(100*(total-part)/total,1)} %", f"{round(part/total,2)}", f"{round(total/part,2)}"]
+    ch = [correct]+distractors
+    rng.shuffle(ch)
+    expl = f"Proportion = {part}/{total} ≈ {round(part/total,2)} → {correct}."
+    return Question("Proportions et pourcentages", difficulty, stem, ch, ch.index(correct), expl)
+
+
+def _gen_evolutions(difficulty: str, rng: random.Random) -> Question:
+    val = rng.randint(100,500)
+    taux = rng.choice([5,10,20])
+    stem = f"Un prix de {val} € augmente de {taux} %. Quelle est la nouvelle valeur ?"
+    correct = f"{round(val*(1+taux/100),2)}"
+    distractors = [f"{round(val*(1-taux/100),2)}", f"{val+taux}", f"{round(val*(taux/100),2)}"]
+    ch = [correct]+distractors
+    rng.shuffle(ch)
+    expl = f"Nouvelle valeur = {val}×(1+{taux}/100) = {correct}."
+    return Question("Évolutions et variations", difficulty, stem, ch, ch.index(correct), expl)
+
+
+def _gen_fonctions(difficulty: str, rng: random.Random) -> Question:
+    a = rng.randint(1,5)
+    b = rng.randint(-5,5)
+    x0 = rng.randint(-3,3)
+    stem = f"Soit f(x) = {a}x + {b}. Quelle est l’image de {x0} par f ?"
+    f_x0 = a*x0+b
+    correct = str(f_x0)
+    distractors = [str(f_x0+1), str(f_x0-1), str(-f_x0)]
+    ch = [correct]+distractors
+    rng.shuffle(ch)
+    expl = f"f({x0}) = {a}×{x0}+{b} = {f_x0}."
+    payload = {"type":"affine","a":a,"b":b,"points":[(x0,f_x0)]}
+    return Question("Fonctions et représentations", difficulty, stem, ch, ch.index(correct), expl, plot=True, plot_payload=payload)
+
+
+def _gen_stats(difficulty: str, rng: random.Random) -> Question:
+    data = [rng.randint(5,15) for _ in range(8)]
+    m = round(statistics.mean(data),1)
+    stem = f"Données : {data}. Quelle est la moyenne arrondie à 0,1 près ?"
+    correct = f"{m}"
+    distractors = [f"{m+0.5}", f"{m-0.5}", f"{round(m+1.0,1)}"]
+    ch = [correct]+distractors
+    rng.shuffle(ch)
+    expl = f"Moyenne = somme/nb = {sum(data)}/{len(data)} = {round(statistics.mean(data),3)} ≈ {m}."
+    payload = {"type":"stats_hist","data":data}
+    return Question("Statistiques", difficulty, stem, ch, ch.index(correct), expl, plot=True, plot_payload=payload)
+
+
+def _gen_proba(difficulty: str, rng: random.Random) -> Question:
+    total = rng.randint(6,12)
+    fav = rng.randint(1,total-1)
+    stem = f"On lance une expérience à {total} issues équiprobables, dont {fav} favorables. Quelle est la probabilité de l’événement ?"
+    correct = f"{fav}/{total}"
+    distractors = [f"{total}/{fav}", f"{fav}/{fav+1}", f"{total-fav}/{total}"]
+    ch = [correct]+distractors
+    rng.shuffle(ch)
+    expl = f"P(A) = {fav}/{total} car {fav} issues favorables sur {total} issues équiprobables."
+    return Question("Probabilités", difficulty, stem, ch, ch.index(correct), expl)
@@
-GENS = {
-    "Fonctions": _gen_fonctions,
-    "Suites": _gen_suites,
-    "Statistiques & Probabilités": _gen_stats_prob,
-    "Géométrie analytique": _gen_geo,
-    "Calcul numérique": _gen_calc,
-    "Équations/Ineq.": _gen_eq_ineq,
-}
+GENS = {
+    "Calcul numérique et algébrique": _gen_calc_num,
+    "Proportions et pourcentages": _gen_proportions,
+    "Évolutions et variations": _gen_evolutions,
+    "Fonctions et représentations": _gen_fonctions,
+    "Statistiques": _gen_stats,
+    "Probabilités": _gen_proba,
+}
