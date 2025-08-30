# -*- coding: utf-8 -*-
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
import random, re, math, statistics
import numpy as np

# =========================
# Thèmes officiels du BO
# =========================
THEMES = [
    "Calcul numérique et algébrique",
    "Proportions et pourcentages",
    "Évolutions et variations",
    "Fonctions et représentations",
    "Statistiques",
    "Probabilités"
]

Difficulty = ["Facile", "Moyen", "Difficile"]

# =========================
# Modèle de Question
# =========================
@dataclass
class Question:
    theme: str
    difficulty: str
    stem: str
    choices: List[str]
    correct_index: int
    explanation: str
    plot: bool = False
    plot_payload: Optional[Dict] = None

# =========================
# Fonctions utilitaires
# =========================
def _norm(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s

def _unique_choices(choices: List[str]) -> bool:
    seen = set()
    for c in choices:
        k = _norm(c)
        if k in seen:
            return False
        seen.add(k)
    return True

def validate(q: Question) -> Tuple[bool, List[str]]:
    """Valide une question (unicité des choix, explication non vide, etc.)."""
    issues = []
    if q.theme not in THEMES:
        issues.append("Thème inconnu.")
    if q.difficulty not in Difficulty:
        issues.append("Difficulté invalide.")
    if len(q.choices) != 4:
        issues.append("Nombre de choix différent de 4.")
    if not (0 <= q.correct_index < 4):
        issues.append("Index de la bonne réponse hors bornes.")
    if not _unique_choices(q.choices):
        issues.append("Doublon dans les réponses proposées.")
    if not q.explanation or len(_norm(q.explanation)) < 8:
        issues.append("Explication manquante ou trop courte.")
    if q.plot and not q.plot_payload:
        issues.append("Graphique demandé sans paramètres.")
    return (len(issues) == 0, issues)

# =========================
# GÉNÉRATEURS PAR THÈME
# =========================
def _gen_calc_num(difficulty: str, rng: random.Random) -> Question:
    """Calcul numérique et algébrique : puissances, fractions, développements."""
    if difficulty == "Facile":
        a, b = rng.randint(2, 5), rng.randint(2, 5)
        stem = f"Calculer : {a}² + {b}²."
        correct = str(a**2 + b**2)
        distractors = [str((a+b)**2), str(a**2 - b**2), str(a*b)]
        expl = f"{a}² + {b}² = {a**2} + {b**2} = {a**2+b**2}."
    elif difficulty == "Moyen":
        a, b = rng.randint(2, 5), rng.randint(2, 4)
        stem = f"Développer : ({a}x + {b})²."
        correct = f"{a**2}x² + {2*a*b}x + {b**2}"
        distractors = [f"{a**2}x² + {b**2}", f"{a**2}x² + {2*a*b}x", f"{(a+b)**2}"]
        expl = f"Identité remarquable : (ax+b)² = a²x²+2abx+b²."
    else:  # Difficile
        a, b, c = rng.randint(2,4), rng.randint(2,4), rng.randint(2,4)
        stem = f"Factoriser : {a}x² + {b}x."
        correct = f"x({a}x+{b})"
        distractors = [f"({a}x+{b})(x+1)", f"{a}x(x+{b})", f"x²({a}+{b})"]
        expl = f"Factorisation par x : {a}x²+{b}x = x({a}x+{b})."
    choices = [correct] + distractors
    rng.shuffle(choices)
    return Question("Calcul numérique et algébrique", difficulty, stem, choices, choices.index(correct), expl)

def _gen_proportions(difficulty: str, rng: random.Random) -> Question:
    total = rng.randint(50, 150)
    part = rng.randint(10, total-10)
    if difficulty == "Facile":
        stem = f"Dans une classe de {total} élèves, {part} sont des filles. Quelle proportion cela représente-t-il ?"
        correct = f"{round(100*part/total,1)} %"
        distractors = [f"{round(100*(total-part)/total,1)} %", f"{round(part/total,2)}", f"{round(total/part,2)}"]
        expl = f"Proportion = {part}/{total} = {round(part/total,2)} → {correct}."
    elif difficulty == "Moyen":
        stem = f"Exprimer la proportion {part}/{total} sous forme de pourcentage."
        correct = f"{round(100*part/total,1)} %"
        distractors = [f"{part}/{total}", f"{round(part/total,2)}", f"{round(total/part,2)} %"]
        expl = f"Proportion = {part}/{total} = {round(part/total,2)} = {correct}."
    else:  # Difficile
        stem = f"On a {part} éléments sur {total}. Donner la fraction irréductible."
        from math import gcd
        g = gcd(part, total)
        correct = f"{part//g}/{total//g}"
        distractors = [f"{part}/{total}", f"{total}/{part}", f"{part+1}/{total}"]
        expl = f"Fraction irréductible : {part}/{total} ÷ {g} = {correct}."
    ch = [correct] + distractors
    rng.shuffle(ch)
    return Question("Proportions et pourcentages", difficulty, stem, ch, ch.index(correct), expl)

def _gen_evolutions(difficulty: str, rng: random.Random) -> Question:
    val = rng.randint(50, 500)
    if difficulty == "Facile":
        taux = rng.choice([5, 10])
    elif difficulty == "Moyen":
        taux = rng.choice([15, 20])
    else:
        taux = rng.choice([25, 30, 40])
    stem = f"Un prix de {val} € augmente de {taux} %. Quelle est la nouvelle valeur ?"
    correct = f"{round(val*(1+taux/100),2)}"
    distractors = [f"{round(val*(1-taux/100),2)}", f"{val+taux}", f"{round(val*(taux/100),2)}"]
    ch = [correct] + distractors
    rng.shuffle(ch)
    expl = f"Nouvelle valeur = {val}×(1+{taux}/100) = {correct}."
    return Question("Évolutions et variations", difficulty, stem, ch, ch.index(correct), expl)

def _gen_fonctions(difficulty: str, rng: random.Random) -> Question:
    if difficulty == "Facile":
        a, b, x0 = rng.randint(1, 5), rng.randint(-5, 5), rng.randint(-3, 3)
        stem = f"Soit f(x) = {a}x + {b}. Quelle est l’image de {x0} par f ?"
        f_x0 = a*x0 + b
        correct = str(f_x0)
        distractors = [str(f_x0+1), str(f_x0-1), str(-f_x0)]
        expl = f"f({x0}) = {a}×{x0}+{b} = {f_x0}."
    elif difficulty == "Moyen":
        a, b = rng.randint(1, 5), rng.randint(-5, 5)
        stem = f"Quelle est l’équation réduite de la droite de coefficient directeur {a} passant par (0,{b}) ?"
        correct = f"y = {a}x + {b}"
        distractors = [f"y = {b}x + {a}", f"y = {a}x - {b}", f"y = {a+b}x"]
        expl = f"Une droite de pente {a} et ordonnée à l’origine {b} : y={a}x+{b}."
    else:  # Difficile
        x1,y1 = rng.randint(-4,4), rng.randint(-4,4)
        x2,y2 = rng.randint(-4,4), rng.randint(-4,4)
        a = (y2-y1)/(x2-x1) if x2!=x1 else 1
        b = y1 - a*x1
        stem = f"Quelle est l’équation de la droite passant par A({x1},{y1}) et B({x2},{y2}) ?"
        correct = f"y = {round(a,2)}x + {round(b,2)}"
        distractors = [f"y = {round(-a,2)}x + {round(b,2)}", f"y = {round(a,2)}x", f"y = {round(a,2)}x - {round(b,2)}"]
        expl = f"Coefficient directeur a = (y2-y1)/(x2-x1) = {round(a,2)}, donc y={round(a,2)}x+{round(b,2)}."
    ch = [correct] + distractors
    rng.shuffle(ch)
    payload = {"type":"affine","a":a,"b":b,"points":[] } if difficulty!="Facile" else {"type":"affine","a":a,"b":b,"points":[(x0,f_x0)]}
    return Question("Fonctions et représentations", difficulty, stem, ch, ch.index(correct), expl, plot=True, plot_payload=payload)

def _gen_stats(difficulty: str, rng: random.Random) -> Question:
    data = [rng.randint(5, 15) for _ in range(10)]
    if difficulty == "Facile":
        m = round(statistics.mean(data),1)
        stem = f"Données : {data}. Quelle est la moyenne arrondie à 0,1 près ?"
        correct = f"{m}"
        distractors = [f"{m+0.5}", f"{m-0.5}", f"{round(m+1.0,1)}"]
        expl = f"Moyenne = {sum(data)}/{len(data)} = {round(statistics.mean(data),2)} ≈ {m}."
    elif difficulty == "Moyen":
        stem = f"Données : {data}. Quelle est la médiane ?"
        correct = str(statistics.median(data))
        distractors = [str(min(data)), str(max(data)), str(round(statistics.mean(data),1))]
        expl = "La médiane sépare la série ordonnée en deux parties égales."
    else:  # Difficile
        stem = f"Données : {data}. Quel est le premier quartile (Q1) ?"
        q1 = np.percentile(sorted(data),25)
        correct = str(q1)
        distractors = [str(np.percentile(sorted(data),50)), str(min(data)), str(max(data))]
        expl = "Q1 est la valeur qui sépare 25% des données les plus petites."
    ch = [correct] + distractors
    rng.shuffle(ch)
    payload = {"type":"stats_hist","data":data}
    return Question("Statistiques", difficulty, stem, ch, ch.index(correct), expl, plot=True, plot_payload=payload)

def _gen_proba(difficulty: str, rng: random.Random) -> Question:
    total = rng.randint(6, 12)
    fav = rng.randint(1, total-1)
    if difficulty == "Facile":
        stem = f"On lance une expérience à {total} issues équiprobables, dont {fav} favorables. Quelle est la probabilité ?"
        correct = f"{fav}/{total}"
        distractors = [f"{total}/{fav}", f"{fav}/{fav+1}", f"{total-fav}/{total}"]
        expl = f"P(A)={fav}/{total} car {fav} issues favorables."
    elif difficulty == "Moyen":
        stem = f"Un dé équilibré à 6 faces. Quelle est la probabilité d’obtenir un multiple de 3 ?"
        correct = "2/6"
        distractors = ["1/6","3/6","4/6"]
        expl = "Multiples de 3 entre 1 et 6 : {3,6}, donc 2/6."
    else:  # Difficile
        stem = "On tire une carte dans un jeu de 52 cartes. Probabilité d’obtenir un cœur ou un carreau ?"
        correct = "26/52"
        distractors = ["13/52","39/52","1/4"]
        expl = "Il y a 26 cartes rouges (cœurs+carreaux) sur 52, donc 26/52."
    ch = [correct] + distractors
    rng.shuffle(ch)
    return Question("Probabilités", difficulty, stem, ch, ch.index(correct), expl)

# =========================
# Générateurs enregistrés
# =========================
GENS = {
    "Calcul numérique et algébrique": _gen_calc_num,
    "Proportions et pourcentages": _gen_proportions,
    "Évolutions et variations": _gen_evolutions,
    "Fonctions et représentations": _gen_fonctions,
    "Statistiques": _gen_stats,
    "Probabilités": _gen_proba,
}

# =========================
# Génération des séries
# =========================
def generate(theme: str, difficulty: str, rng: random.Random) -> Question:
    q = GENS[theme](difficulty, rng)
    ok, _ = validate(q)
    if not ok:
        for _ in range(3):
            q = GENS[theme](difficulty, rng)
            ok, _ = validate(q)
            if ok:
                break
    return q

def generate_set(theme: Optional[str], difficulty: str, n: int, seed: int) -> List[Question]:
    rng = random.Random(seed)
    themes = [theme] if theme and theme != "Auto" else THEMES
    qs = []
    while len(qs) < n:
        t = rng.choice(themes)
        q = generate(t, difficulty, rng)
        if not any(_norm(q.stem) == _norm(existing.stem) for existing in qs):
            qs.append(q)
    return qs[:n]

def generate_exam(seed: int) -> List[Question]:
    rng = random.Random(seed)
    qs = []
    counts = {t:0 for t in THEMES}
    while len(qs) < 12:
        t = rng.choice(THEMES)
        if counts[t] >= 3:
            continue
        diff = rng.choice(Difficulty)
        q = generate(t, diff, rng)
        if not any(_norm(q.stem) == _norm(existing.stem) for existing in qs):
            qs.append(q)
            counts[t] += 1
    return qs[:12]

def to_dict(q: Question) -> Dict:
    return asdict(q)
