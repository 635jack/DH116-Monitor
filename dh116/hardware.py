#!/usr/bin/env python3
"""
hardware.py — topologie et bornes de la main DH116.

Que des données, aucune logique. La correspondance moteur → zone tactile a été
recoupée avec le découpage mesuré des trames : elles concordent.

Aucun moteur n'est déclaré en panne ici. Une main d'exemplaire donné peut avoir
un actionneur mort ; cela se dit à l'exécution (``--exclure 1``), pas dans le
code, sinon le défaut d'une main devient une contrainte pour toutes.
"""
from __future__ import annotations

MOTOR_IDS = (1, 2, 3, 4, 5, 6)

MOTOR_NAMES = {
    1: "pouce_flexion",
    2: "pouce_pivot",
    3: "auriculaire",
    4: "annulaire",
    5: "majeur",
    6: "index",
}

#: Le pivot du pouce n'est pas un fléchisseur : il fait pivoter le pouce pour
#: l'amener en face des autres doigts.
THUMB_PIVOT = 2

#: Consigne du pivot qui amène le pouce en opposition, face au majeur. Relevée
#: à l'œil au banc : à 0 le pouce est relevé, hors du plan de préhension.
THUMB_OPPOSITION = 8000

#: Moteurs qui referment la main.
FLEXORS = tuple(m for m in MOTOR_IDS if m != THUMB_PIVOT)


def flexors(excluded: tuple[int, ...] = ()) -> tuple[int, ...]:
    """Fléchisseurs pilotables, une fois retirés les moteurs exclus."""
    return tuple(m for m in FLEXORS if m not in excluded)


def motors(excluded: tuple[int, ...] = ()) -> tuple[int, ...]:
    """Tous les moteurs pilotables, pivot compris."""
    return tuple(m for m in MOTOR_IDS if m not in excluded)


#: Moteur → préfixe des zones tactiles qu'il met en contact.
MOTOR_TO_ZONE = {1: "thumb", 3: "little", 4: "ring", 5: "middle", 6: "index"}


def zones_of(motor: int) -> tuple[str, ...]:
    """
    Zones surveillées pour un moteur donné.

    La pulpe touche en premier quand l'objet repose à la base des doigts, le
    bout quand la phalange s'enroule.
    """
    prefix = MOTOR_TO_ZONE.get(motor)
    if prefix is None:
        return ()
    # Le pouce et l'auriculaire n'ont qu'un capteur, sans pulpe distincte.
    if prefix in ("thumb", "little"):
        return (prefix,)
    return (f"{prefix}.pad", f"{prefix}.tip")


# ── Bornes ────────────────────────────────────────────────────────────────────

POSITION_OPEN = 0
#: Garde-fou mécanique de fermeture. Le SDK accepte 10000 ; on n'y va pas.
POSITION_MAX = 8500

VELOCITY_OPEN = 10000
VELOCITY_CLOSE = 500

#: Courant maximum, en pour-mille. 1000 est le plafond du variateur.
FULL_CURRENT = 1000
#: Maintien après saisie : les moteurs calés sur un objet chauffent.
HOLD_CURRENT = 150
#: Approche d'un objet inconnu, volontairement basse : le doigt cale contre
#: l'objet au lieu de l'écraser.
APPROACH_CURRENT = 400
#: Plafond pour une saisie qui serre vraiment. Mesuré : à 400 les doigts
#: s'arrêtent sur leur propre plafond de couple avant de toucher l'objet.
GRASP_CURRENT = 800

#: Courant au-delà duquel un doigt immobile pousse contre quelque chose. En
#: dessous, une immobilité signifie que l'ordre n'est pas passé.
SEUIL_BLOQUE = 500
#: Tolérance sur la position atteinte, et seuil sous lequel on considère qu'un
#: moteur n'a pas bougé du tout.
TOLERANCE = 60
SEUIL_IMMOBILE = 100
