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
    b = rng.randi
