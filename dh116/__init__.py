"""
dh116 — pilotage et lecture tactile de la main DH116, sans ROS.

Trois commandes, installées avec le paquet :

* ``dh116-tactile``     pression des zones tactiles, en direct dans le terminal
* ``dh116-pilote``      pilotage des moteurs, en ligne de commande
* ``dh116-diagnostic``  les moteurs répondent-ils ? réponse en un tableau

Le SDK constructeur ne sert qu'à monter EtherCAT, réveiller la main et basculer
ses trames en mode capteur. Le contenu des trames est décodé ici, dans
:mod:`dh116.tpdo`, à partir d'une table établie par la mesure.
"""

__version__ = "1.0.0"
