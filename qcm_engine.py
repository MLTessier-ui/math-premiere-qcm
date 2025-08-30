# -*- coding: utf-8 -*-
import random
import numpy as np

# ===============================
# Classes
# ===============================
class Question:
    def __init__(self, theme, difficulty, stem, choices, correct_index, explanation, plot=False, plot_payload=None):
        self.theme = theme
        self.difficulty = difficulty
        self.stem = stem
        self.choices = choices
        self.correct_index = correct_index
        self.explanation = explanation
        self.plot = plot
        self.plot_payload = plot_payload or {}

THEMES = [
    "Calcul numérique et algébrique",
    "Proportions et pourcentages",
    "Évolutions et variations",
    "Fonctions et représentations",
    "Statistiques",
    "Probabilités"
]

Difficulty = ["Facile", "Moyen", "Difficile"]

# ===============================
# Outils utilitaires
# ===============================
def _norm(s: str) -> str:
    return str(s).strip().lower()

def validate(q: Question):
    issues = []
    if len(q.choices) != 4:
        issues.append("Pas 4 choix")
    if not (0 <= q.correct_index < 4):
        issues.append("Index hors bornes")
    normed = [_norm(c) for c in q.choices]
    if len(set(normed)) != 4:
        issues.append("Choix non uniques")
    if not q.explanation:
        issues.append("Explication manquante")
    return (len(issues) == 0), issues

def to_dict(q: Question) -> dict:
    return {
        "theme": q.theme,
        "difficulty": q.difficulty,
        "stem": q.stem,
        "choices": q.choices,
        "correct_index": q.correct_index,
        "explanation": q.explanation,
        "plot": q.plot,
        "plot_payload": q.plot_payload
    }

# ===============================
# Générateurs par thème
# ===============================

def _gen_calcul(difficulty, rng):
    a = rng.randint(2, 12)
    b = rng.randint(2, 12)
    if difficulty == "Facile":
        stem = f"Calcule {a} × {b}"
        correct = a * b
    elif difficulty == "Moyen":
        stem = f"Calcule ({a}+{b})²"
        correct = (a+b)**2
    else:
        stem = f"Développe ({a}−{b})({a}+{b})"
        correct = a**2 - b**2
    choices = [correct, correct+1, correct-1, correct+2]
    rng.shuffle(choices)
    return Question("Calcul numérique et algébrique", difficulty, stem, [str(c) for c in choices], choices.index(correct), f"On applique les règles de calcul.")

def _gen_proportions(difficulty, rng):
    base = rng.randint(50,200)
    pct = rng.choice([10,20,25,50])
    if difficulty == "Facile":
        stem = f"Augmenter {base} de {pct}%"
        correct = base*(1+pct/100)
    elif difficulty == "Moyen":
        stem = f"Réduire {base} de {pct}%"
        correct = base*(1-pct/100)
    else:
        stem = f"Augmenter {base} de {pct}% puis réduire le résultat de {pct}%"
        correct = base*(1+pct/100)*(1-pct/100)
    choices = [correct, correct+10, correct-10, round(correct*1.1)]
    rng.shuffle(choices)
    return Question("Proportions et pourcentages", difficulty, stem, [str(round(c,2)) for c in choices], choices.index(correct), "On applique les pourcentages successivement.")

def _gen_evolutions(difficulty, rng):
    u0 = rng.randint(100,200)
    r = rng.randint(2,10)
    if difficulty == "Facile":
        stem = f"Suite arithmétique : u₀={u0}, raison r={r}. Calculer u₁."
        correct = u0+r
    elif difficulty == "Moyen":
        stem = f"Suite arithmétique : u₀={u0}, r={r}. Calculer u₅."
        correct = u0+5*r
    else:
        stem = f"Suite géométrique : u₀={u0}, q={r/10}. Calculer u₃."
        correct = u0*(r/10)**3
    choices = [correct, correct+1, correct-1, correct+5]
    rng.shuffle(choices)
    return Question("Évolutions et variations", difficulty, stem, [str(round(c,2)) for c in choices], choices.index(correct), "On utilise la formule explicite des suites.")

def _gen_fonctions(difficulty, rng):
    a = rng.randint(1,5)
    b = rng.randint(-5,5)
    stem = f"On considère une fonction affine représentée ci-dessous. Quelle est son expression algébrique ?"
    correct = f"{a}x+{b}" if b>=0 else f"{a}x{b}"
    distractors = [f"{a+1}x+{b}", f"{a}x+{b+1}", f"{a-1}x+{b}"]
    choices = [correct]+distractors
    rng.shuffle(choices)
    payload = {"type":"affine","a":a,"b":b,"points":[]}
    return Question("Fonctions et représentations", difficulty, stem, choices, choices.index(correct), "On lit le coefficient directeur et l'ordonnée à l'origine sur le graphique.", plot=True, plot_payload=payload)

def _gen_stats(difficulty, rng):
    data = [rng.randint(5,20) for _ in range(10)]
    mean = sum(data)/len(data)
    if difficulty=="Facile":
        stem = f"On a relevé 10 valeurs (voir histogramme). Quelle est leur moyenne arrondie à l'unité ?"
        correct = round(mean)
        distractors = [correct+1, correct-1, correct+2]
    elif difficulty=="Moyen":
        stem = f"Quelle est la médiane de cette série de 10 valeurs (voir histogramme) ?"
        sorted_data = sorted(data)
        correct = (sorted_data[4]+sorted_data[5])/2
        distractors = [correct+1, correct-1, sorted_data[0]]
    else:
        stem = f"Quelle est l'étendue de cette série (voir histogramme) ?"
        correct = max(data)-min(data)
        distractors = [correct+1, correct-1, correct+2]
    choices = [correct]+distractors
    rng.shuffle(choices)
    payload = {"type":"stats_hist","data":data}
    return Question("Statistiques", difficulty, stem, [str(round(c,2)) for c in choices], choices.index(correct), "On utilise les définitions : moyenne, médiane, étendue.", plot=True, plot_payload=payload)

def _gen_probabilites(difficulty, rng):
    n = 6
    if difficulty=="Facile":
        stem = "On lance un dé équilibré. Quelle est la probabilité d'obtenir un 6 ?"
        correct = 1/n
        distractors = [1/2,1/3,1/4]
    elif difficulty=="Moyen":
        stem = "On lance un dé équilibré. Quelle est la probabilité d'obtenir un nombre pair ?"
        correct = 3/n
        distractors = [2/n,4/n,5/n]
    else:
        stem = "On lance deux dés équilibrés. Quelle est la probabilité d'obtenir une somme égale à 7 ?"
        correct = 6/36
        distractors = [1/6,1/12,1/18]
    choices = [correct]+distractors
    rng.shuffle(choices)
    return Question("Probabilités", difficulty, stem, [str(round(c,2)) for c in choices], choices.index(correct), "On compte les issues favorables et on divise par le nombre total de cas.")

# ===============================
# Dispatcher
# ===============================
GENERATORS = {
    "Calcul numérique et algébrique": _gen_calcul,
    "Proportions et pourcentages": _gen_proportions,
    "Évolutions et variations": _gen_evolutions,
    "Fonctions et représentations": _gen_fonctions,
    "Statistiques": _gen_stats,
    "Probabilités": _gen_probabilites,
}

def generate_set(theme, difficulty, n, seed=None):
    rng = random.Random(seed)
    out = []
    themes = THEMES if theme=="Auto" else [theme]
    while len(out)<n:
        th = rng.choice(themes)
        q = GENERATORS[th](difficulty, rng)
        if q.stem not in [qq.stem for qq in out]:
            out.append(q)
    return out

def generate_exam(seed=None):
    rng = random.Random(seed)
    out = []
    for th in THEMES:
        q = GENERATORS[th](rng.choice(Difficulty), rng)
        out.append(q)
    # compléter à 12
    while len(out)<12:
        th = rng.choice(THEMES)
        q = GENERATORS[th](rng.choice(Difficulty), rng)
        if q.stem not in [qq.stem for qq in out]:
            out.append(q)
    rng.shuffle(out)
    return out
