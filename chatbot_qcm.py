*** /dev/null
--- a/qcm_engine.py
+from dataclasses import dataclass, asdict
+from typing import List, Dict, Tuple, Optional
+import random, re, math, statistics
+import difflib
+import numpy as np
+
+THEMES = [
+    "Fonctions", "Suites", "Statistiques & Probabilités",
+    "Géométrie analytique", "Calcul numérique", "Équations/Ineq."
+]
+
+Difficulty = ["Facile","Moyen","Difficile"]
+
+@dataclass
+class Question:
+    theme: str
+    difficulty: str
+    stem: str
+    choices: List[str]
+    correct_index: int
+    explanation: str
+    plot: bool = False            # si True, on générera un graphique
+    plot_payload: Optional[Dict]=None  # paramètres pour le tracé
+
+def _norm(s: str) -> str:
+    s = s.lower().strip()
+    s = re.sub(r"\s+", " ", s)
+    s = re.sub(r"[’'`]", "'", s)
+    return s
+
+def _similar(a: str, b: str, thresh: float=0.92) -> bool:
+    return difflib.SequenceMatcher(a=_norm(a), b=_norm(b)).ratio() >= thresh
+
+def _unique_choices(choices: List[str]) -> bool:
+    seen = set()
+    for c in choices:
+        k = _norm(c)
+        if k in seen: return False
+        seen.add(k)
+    return True
+
+def validate(q: Question) -> Tuple[bool, List[str]]:
+    issues = []
+    if q.theme not in THEMES:
+        issues.append("Thème inconnu.")
+    if q.difficulty not in Difficulty:
+        issues.append("Difficulté invalide.")
+    if len(q.choices) != 4:
+        issues.append("Nombre de choix différent de 4.")
+    if not (0 <= q.correct_index < 4):
+        issues.append("Index de la bonne réponse hors bornes.")
+    if not _unique_choices(q.choices):
+        issues.append("Doublon dans les réponses proposées.")
+    if not q.explanation or len(_norm(q.explanation)) < 8:
+        issues.append("Explication manquante ou trop courte.")
+    if q.plot and not q.plot_payload:
+        issues.append("Graphique demandé sans paramètres.")
+    return (len(issues) == 0, issues)
+
+def dedupe_questions(qs: List[Question]) -> List[Question]:
+    kept = []
+    for q in qs:
+        if any(_similar(q.stem, k.stem) for k in kept):
+            continue
+        kept.append(q)
+    return kept
+
+# -----------------------
+# GÉNÉRATEURS PAR THÈME
+# -----------------------
+def _gen_fonctions(difficulty: str, rng: random.Random) -> Question:
+    # Fonctions affines / quadratiques simples
+    if difficulty == "Facile":
+        a = rng.randint(-5,5) or 2
+        b = rng.randint(-6,6)
+        x0 = rng.randint(-4,4)
+        f_x0 = a*x0 + b
+        stem = f"Soit f(x) = {a}x + {b}. Que vaut f({x0}) ?"
+        correct = str(f_x0)
+        distractors = list({str(f_x0 + d) for d in {rng.randint(-5,5), rng.randint(1,7), -rng.randint(1,7)} if d!=0})
+        while len(distractors) < 3:
+            distractors.append(str(f_x0 + rng.choice([2,-3,5,-4])))
+        choices = [correct] + distractors[:3]
+        rng.shuffle(choices)
+        correct_index = choices.index(correct)
+        expl = f"On calcule f({x0}) = {a}×{x0} + {b} = {a*x0} + {b} = {f_x0}."
+        payload = {"type":"affine","a":a,"b":b,"points":[(x0,f_x0)]}
+        return Question("Fonctions", difficulty, stem, choices, correct_index, expl, plot=True, plot_payload=payload)
+    else:
+        # Quadratique : sommet / image / racines approximatives
+        p = rng.randint(-3,3)
+        qv = rng.randint(-5,5)
+        # f(x)= (x - p)^2 + q
+        x0 = rng.randint(-4,4)
+        f_x0 = (x0 - p)**2 + qv
+        stem = f"Soit f(x) = (x - {p})² + {qv}. Que vaut f({x0}) ?"
+        correct = str(f_x0)
+        distractors = list({str((x0 + p)**2 + qv), str((x0 - p)**2 - qv), str(-(x0 - p)**2 + qv)})
+        while len(distractors) < 3:
+            distractors.append(str(f_x0 + rng.choice([-3,-2,2,3,5])))
+        choices = [correct] + distractors[:3]
+        rng.shuffle(choices)
+        correct_index = choices.index(correct)
+        expl = f"f({x0}) = ({x0} - {p})² + {qv} = {(x0 - p)**2} + {qv} = {f_x0}."
+        payload = {"type":"quadratique","p":p,"q":qv,"points":[(x0,f_x0)]}
+        return Question("Fonctions", difficulty, stem, choices, correct_index, expl, plot=True, plot_payload=payload)
+
+def _gen_suites(difficulty: str, rng: random.Random) -> Question:
+    if difficulty == "Facile":
+        u0 = rng.randint(-5,5)
+        r = rng.randint(-4,6)
+        n = rng.randint(3,8)
+        stem = f"Suite arithmétique de premier terme u0={u0} et raison r={r}. Calculer u{n}."
+        u_n = u0 + n*r
+        correct = str(u_n)
+        distractors = [str(u0 + (n+1)*r), str(u0 + (n-1)*r), str(u0*r + n)]
+        choices = [correct]+distractors
+        rng.shuffle(choices)
+        return Question("Suites", difficulty, stem, choices, choices.index(correct),
+                        f"u_n = u0 + n·r = {u0} + {n}×{r} = {u_n}.")
+    else:
+        u0 = rng.randint(1,5)
+        q = rng.choice([2,3,1/2,1/3])
+        n = rng.randint(3,6)
+        stem = f"Suite géométrique u0={u0} et raison q={q}. Calculer u{n}."
+        u_n = u0*(q**n)
+        correct = str(u_n)
+        distractors = [str(u0*(q**(n-1))), str(u0*q*n), str(u0+q**n)]
+        ch = [correct]+distractors
+        rng.shuffle(ch)
+        return Question("Suites", difficulty, stem, ch, ch.index(correct),
+                        f"u_n = u0·qⁿ = {u0}×{q}^{n} = {u_n}.")
+
+def _gen_stats_prob(difficulty: str, rng: random.Random) -> Question:
+    data = [rng.randint(5,20) for _ in range(rng.randint(6,10))]
+    stem = f"Données : {data}. Quelle est la moyenne arrondie à 0,1 près ?"
+    m = statistics.mean(data)
+    correct_val = round(m,1)
+    correct = f"{correct_val}"
+    distractors = [f"{round(m+0.4,1)}", f"{round(m-0.4,1)}", f"{round(m+1.0,1)}"]
+    ch = [correct]+distractors
+    rng.shuffle(ch)
+    payload = {"type":"stats_hist","data":data}
+    return Question("Statistiques & Probabilités", difficulty, stem, ch, ch.index(correct),
+                    f"Moyenne = (somme des valeurs)/effectif = {sum(data)}/{len(data)} ≈ {round(m,3)} → {correct_val}.",
+                    plot=True, plot_payload=payload)
+
+def _gen_geo(difficulty: str, rng: random.Random) -> Question:
+    x1,y1 = rng.randint(-4,4), rng.randint(-4,4)
+    x2,y2 = rng.randint(-4,4), rng.randint(-4,4)
+    stem = f"Dans le plan, A({x1},{y1}) et B({x2},{y2}). Quelle est la distance AB (au dixième) ?"
+    d = math.hypot(x2-x1, y2-y1)
+    correct = f"{round(d,1)}"
+    distractors = [f"{round(abs(x2-x1)+abs(y2-y1),1)}", f"{round(d+1.0,1)}", f"{round(abs(d-1.0),1)}"]
+    ch = [correct]+distractors
+    rng.shuffle(ch)
+    return Question("Géométrie analytique", difficulty, stem, ch, ch.index(correct),
+                    f"AB = √((x₂-x₁)²+(y₂-y₁)²) = √(({x2}-{x1})²+({y2}-{y1})²) = {round(d,3)} → {round(d,1)}.")
+
+def _gen_calc(difficulty: str, rng: random.Random) -> Question:
+    p = rng.randint(5,30)
+    val = rng.randint(50,300)
+    stem = f"Une quantité de {val} augmente de {p}%. Quelle est la nouvelle valeur ?"
+    correct = f"{round(val*(1+p/100),2)}"
+    distractors = [f"{round(val*(1-p/100),2)}", f"{round(val + p,2)}", f"{round(val*(p/100),2)}"]
+    ch = [correct]+distractors
+    rng.shuffle(ch)
+    return Question("Calcul numérique", "Facile", stem, ch, ch.index(correct),
+                    f"Nouvelle valeur = {val}×(1+{p}/100) = {correct}.")
+
+def _gen_eq_ineq(difficulty: str, rng: random.Random) -> Question:
+    a = rng.randint(1,6)
+    b = rng.randint(-8,8)
+    c = rng.randint(-6,6)
+    stem = f"Résoudre l'équation {a}x + {b} = {c}."
+    x = (c-b)/a
+    correct = f"x = {x}"
+    distractors = [f"x = {c+b}", f"x = {(c+b)/a}", f"x = {(b-c)/a}"]
+    ch = [correct]+distractors
+    rng.shuffle(ch)
+    return Question("Équations/Ineq.", "Facile", stem, ch, ch.index(correct),
+                    f"{a}x = {c}-{b} ⇒ x = ({c}-{b})/{a} = {x}.")
+
+GENS = {
+    "Fonctions": _gen_fonctions,
+    "Suites": _gen_suites,
+    "Statistiques & Probabilités": _gen_stats_prob,
+    "Géométrie analytique": _gen_geo,
+    "Calcul numérique": _gen_calc,
+    "Équations/Ineq.": _gen_eq_ineq,
+}
+
+def generate(theme: str, difficulty: str, rng: random.Random) -> Question:
+    q = GENS[theme](difficulty, rng)
+    ok, issues = validate(q)
+    if not ok:
+        # régénération simple (filet de sécurité)
+        for _ in range(3):
+            q = GENS[theme](difficulty, rng)
+            ok, issues = validate(q)
+            if ok: break
+    return q
+
+def generate_set(theme: Optional[str], difficulty: str, n: int, seed: int) -> List[Question]:
+    rng = random.Random(seed)
+    themes = [theme] if theme and theme != "Auto" else THEMES
+    qs = []
+    while len(qs) < n:
+        t = rng.choice(themes)
+        q = generate(t, difficulty, rng)
+        qs.append(q)
+        qs = dedupe_questions(qs)
+    return qs[:n]
+
+def generate_exam(seed: int) -> List[Question]:
+    rng = random.Random(seed)
+    # 12 questions, au moins 1 par thème, pas de répétition de thème > 3
+    themes_cycle = THEMES * 2
+    rng.shuffle(themes_cycle)
+    qs = []
+    counts = {t:0 for t in THEMES}
+    i = 0
+    while len(qs) < 12 and i < 50:
+        t = themes_cycle[i % len(themes_cycle)]
+        if counts[t] >= 3: 
+            i += 1
+            continue
+        diff = rng.choice(Difficulty)
+        q = generate(t, diff, rng)
+        qs.append(q); counts[t]+=1; i+=1
+        qs = dedupe_questions(qs)
+    return qs[:12]
+
+def to_dict(q: Question) -> Dict:
+    d = asdict(q)
+    return d
