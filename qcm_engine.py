# -*- coding: utf-8 -*-
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
import random, re, math, statistics, difflib
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
    s = re.sub(r"[’'`]", "'", s)
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
    a = rng.randint(2, 5)
    b = rng.randint(2, 4)
    stem = f"Calculer : ({a}²) × ({b}²)."
    correct = str((a**2) * (b**2))
    distractors = [str((a*b)**2), str(a**2 + b**2), str((a+b)**2)]
    choices = [correct] + distractors
    rng.shuffle(choices)
    expl = f"({a}²)×({b}²) = {a*a}×{b*b} = {int(correct)}."
    return Question("Calcul numérique et algébrique", difficulty, stem, choices, choices.index(correct), expl)

def _gen_proportions(difficulty: str, rng: random.Random) -> Question:
    total = rng.randint(80, 150)
    part = rng.randint(20, 60)
    stem = f"Dans une classe de {total} élèves, {part} sont des filles. Quelle proportion cela représente-t-il ?"
    correct = f"{round(100*part/total,1)} %"
    distractors = [
        f"{round(100*(total-part)/total,1)} %",
        f"{round(part/total,2)}",
        f"{round(total/part,2)}"
    ]
    ch = [correct] + distractors
    rng.shuffle(ch)
    expl = f"Proportion = {part}/{total} ≈ {round(part/total,2)} → {correct}."
    return Question("Proportions et pourcentages", difficulty, stem, ch, ch.index(correct), expl)

def _gen_evolutions(difficulty: str, rng: random.Random) -> Question:
    val = rng.randint(100, 500)
    taux = rng.choice([5, 10, 20])
    stem = f"Un prix de {val} € augmente de {taux} %. Quelle est la nouvelle valeur ?"
    correct = f"{round(val*(1+taux/100),2)}"
    distractors = [
        f"{round(val*(1-taux/100),2)}",
        f"{val+taux}",
        f"{round(val*(taux/100),2)}"
    ]
    ch = [correct] + distractors
    rng.shuffle(ch)
    expl = f"Nouvelle valeur = {val}×(1+{taux}/100) = {correct}."
    return Question("Évolutions et variations", difficulty, stem, ch, ch.index(correct), expl)

def _gen_fonctions(difficulty: str, rng: random.Random) -> Question:
    a = rng.randint(1, 5)
    b = rng.randint(-5, 5)
    x0 = rng.randint(-3, 3)
    stem = f"Soit f(x) = {a}x + {b}. Quelle est l’image de {x0} par f ?"
    f_x0 = a*x0 + b
    correct = str(f_x0)
    distractors = [str(f_x0+1), str(f_x0-1), str(-f_x0)]
    ch = [correct] + distractors
    rng.shuffle(ch)
    expl = f"f({x0}) = {a}×{x0}+{b} = {f_x0}."
    payload = {"type":"affine", "a":a, "b":b, "points":[(x0,f_x0)]}
    return Question("Fonctions et représentations", difficulty, stem, ch, ch.index(correct), expl, plot=True, plot_payload=payload)

def _gen_stats(difficulty: str, rng: random.Random) -> Question:
    data = [rng.randint(5, 15) for _ in range(8)]
    m = round(statistics.mean(data),1)
    stem = f"Données : {data}. Quelle est la moyenne arrondie à 0,1 près ?"
    correct = f"{m}"
    distractors = [f"{m+0.5}", f"{m-0.5}", f"{round(m+1.0,1)}"]
    ch = [correct] + distractors
    rng.shuffle(ch)
    expl = f"Moyenne = somme/nb = {sum(data)}/{len(data)} = {round(statistics.mean(data),3)} ≈ {m}."
    payload = {"type":"stats_hist","data":data}
    return Question("Statistiques", difficulty, stem, ch, ch.index(correct), expl, plot=True, plot_payload=payload)

def _gen_proba(difficulty: str, rng: random.Random) -> Question:
    total = rng.randint(6, 12)
    fav = rng.randint(1, total-1)
    stem = f"On lance une expérience à {total} issues équiprobables, dont {fav} favorables. Quelle est la probabilité de l’événement ?"
    correct = f"{fav}/{total}"
    distractors = [f"{total}/{fav}", f"{fav}/{fav+1}", f"{total-fav}/{total}"]
    ch = [correct] + distractors
    rng.shuffle(ch)
    expl = f"P(A) = {fav}/{total} car {fav} issues favorables sur {total} issues équiprobables."
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
    ok, issues = validate(q)
    if not ok:
        # filet de sécurité
        for _ in range(3):
            q = GENS[theme](difficulty, rng)
            ok, issues = validate(q)
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
        qs.append(q)
        counts[t] += 1
    return qs[:12]

def to_dict(q: Question) -> Dict:
    return asdict(q)
