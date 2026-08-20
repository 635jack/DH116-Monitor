# DH116-Monitor

Pilotage et lecture tactile de la main **DH-Robotics DH116**, en ligne de
commande, sur n'importe quel Linux. Ni ROS, ni service, ni dépendance hors
bibliothèque standard. Le paquet Python s'appelle `dh116`.

## Démonstration

[![Interface temps réel pour la DH116](https://img.youtube.com/vi/f69M3WfV_O4/hqdefault.jpg)](https://youtu.be/f69M3WfV_O4)

<https://youtu.be/f69M3WfV_O4> — retour tactile en direct et pilotage des
doigts, avec la main réelle en incrustation. C'est l'interface `dh116-web` de ce
dépôt.

Le SDK constructeur ne sert qu'à trois choses : monter EtherCAT, réveiller la
main, et basculer ses trames en mode capteur. **Le contenu des trames est
décodé ici**, à partir d'une table établie par la mesure — pas par lecture du
binaire du SDK, qui lit ses champs un octet trop tôt et rend en conséquence une
proximité constante à 1,00 et une force normale erronée.

## Quatre commandes

| commande | rôle |
| :--- | :--- |
| `dh116-web` | interface web : tactile en direct et pilotage, dans un navigateur |
| `dh116-tactile` | pression des neuf zones tactiles, en direct dans le terminal |
| `dh116-pilote` | pilotage des moteurs, interactif |
| `dh116-diagnostic` | les moteurs répondent-ils ? réponse en un tableau, code de sortie exploitable |

## Ce qu'il faut avant de commencer

* **Linux**, Python **3.10 ou plus**.
* Le **SDK constructeur** `LHandProLib` décompressé quelque part (voir plus bas).
* Un **adaptateur Ethernet** relié à la main. Un adaptateur USB convient ; il en
  faut un dédié, EtherCAT prend l'interface entière.
* Les **droits root** : le maître EtherCAT ouvre des sockets raw.

## Installation

Le plus simple est de ne rien installer : le paquet fonctionne depuis son
dossier.

```bash
git clone <ce-dépôt> dh116-cli
cd dh116-cli
sudo python3 -m dh116.cli.diagnostic
```

Pour disposer des commandes courtes partout :

```bash
pip install --user .        # puis dh116-tactile, dh116-pilote, dh116-diagnostic
```

Sur Debian et Ubuntu récents, `pip` refuse d'écrire dans le Python du système
(PEP 668). Deux issues, au choix :

```bash
python3 -m venv .venv && .venv/bin/pip install .   # puis sudo .venv/bin/dh116-pilote
pip install --user --break-system-packages .       # si vous savez ce que vous faites
```

### Où le SDK est cherché

`dh116` cherche, dans l'ordre : le chemin donné par `--sdk-dir`, puis
`~/Leadshine_SDK_original/sdk_lib`, puis quelques emplacements historiques. Il
lui faut **deux choses, cherchées séparément** :

* la bibliothèque `<arch>/lib/libLHandProLib.so`, qui doit correspondre à
  l'architecture de la machine ;
* les modules Python `<arch>/share/LHandProLib/examples/EtherCAT_python/`.

Ils sont cherchés séparément parce que le constructeur ne livre les modules
Python que sous `x86_64`, alors que la `.so` doit suivre l'architecture réelle.
Sur une machine ARM, il faut donc piocher dans les deux arborescences — ce que
`find_sdk()` fait.

```bash
sudo python3 -m dh116.cli.pilote --sdk-dir /opt/LHandProLib/sdk_lib
```

## Usage

### L'interface web

```bash
sudo python3 -m dh116.cli.web --port 8080
```

Puis `http://<machine>:8080`. C'est ce que montre la vidéo : les neuf zones sur
une main dessinée, les 26 points de paume, les courants, et des curseurs pour
chaque moteur avec quelques poses prêtes à l'emploi.

La page ne parle que **HTTP et Server-Sent Events** — pas de websockets, pas de
rosbridge, aucune dépendance : un serveur de la bibliothèque standard et une
page autonome, CSS et JavaScript compris dedans.

Deux comportements attendus, à ne pas prendre pour des défauts :

* La **position affichée ne se rafraîchit qu'une fois le mouvement terminé**.
  La télémétrie n'est pas interrogée pendant le déplacement : l'affichage reste
  sur son ancienne valeur puis saute à la position finale. La main, elle, se
  déplace continûment — c'est visible dans la vidéo.
* Un doigt immobile qui tire plus de 500 ‰ est déclaré **bloqué** : la commande
  n'est pas relancée, et le moteur apparaît dans `bloques`. C'est un obstacle
  mécanique, pas une commande perdue.

La machine n'est joignable que depuis elle-même par défaut. Pour y accéder
d'ailleurs, `--host 0.0.0.0` — en sachant que **l'interface n'a aucune
authentification** : quiconque atteint le port peut refermer les doigts.

### Lire le tactile

```bash
sudo python3 -m dh116.cli.tactile
```

Une barre par canal, la pression maximale, et pour les doigts la force normale,
la force tangentielle, la direction et la proximité. Le zéro est pris au
démarrage, main au repos — sans lui les zones ne sont pas comparables entre
elles, leurs lignes de base diffèrent beaucoup. `Entrée` ou `r` refont le zéro,
`q` quitte.

### Piloter les moteurs

```bash
sudo python3 -m dh116.cli.pilote
```

```
main> 6 4000        l'index à 4000
main> index 4000    pareil, par le nom
main> 5 4000 300    le majeur, à la vitesse 300
main> ouvrir        tous les moteurs à 0
main> fermer | pince | saisie
main> etat          positions, courants, alarmes, contacts tactiles
main> legende       à quoi correspondent les chiffres
main> alarmes | raz consulter et lever les défauts variateur
main> zero          refait le zéro tactile
main> reconnexion   referme et rouvre le bus
main> q             quitter — la main est rouverte avant de rendre le bus
```

### Vérifier que tout répond

```bash
sudo python3 -m dh116.cli.diagnostic                 # tous les moteurs
sudo python3 -m dh116.cli.diagnostic --motor 6 --repeat 5
```

```
moteur          sens         atteint  / cible   course  courant max   verdict
----------------------------------------------------------------------------
index           fermeture       3001     3000     3001          179   ok
index           ouverture          0        0     3001           50   ok
```

Sortie **0** si tout répond, **1** sinon : utilisable dans un script.

## Les positions

Elles sont en **counts codeur**, pas en degrés.

| moteur | doigt | plage |
| ---: | :--- | :--- |
| 1 | flexion du pouce | 0 tendu → 8500 replié |
| 2 | opposition du pouce | 0 à plat → 8000 face aux doigts |
| 3 | auriculaire | 0 tendu → 8500 replié |
| 4 | annulaire | idem |
| 5 | majeur | idem |
| 6 | index | idem |

Environ **4000** referme franchement un doigt, **3000 à 5000** pour saisir selon
la taille de l'objet, au-delà de **6000** il vient au contact de la paume.

## Les zones tactiles

Neuf zones, pas onze. Le SDK en déclare onze : il compte une pulpe au pouce et à
l'auriculaire, **qui n'existent pas** — ces deux doigts n'ont qu'un capteur,
dont le bout et la pulpe excitent les mêmes canaux. En publier onze reviendrait
à dupliquer une mesure.

| zone | canaux |
| :--- | ---: |
| `thumb`, `little` | 5 chacun, plus une voie de **proximité interne** |
| `index`, `middle`, `ring` — `.tip` et `.pad` | 4 par capteur |
| `palm` | 26 points |

Sur notre exemplaire, douze points de paume ne répondaient pas à un balayage
manuel. Ils sont listés dans `PALM_SILENT` **à titre indicatif** et ne sont pas
masqués par défaut : un capteur muet sur une main peut répondre sur une autre.
`--masquer-muets` les met en retrait si vous retrouvez le même comportement.

La **proximité interne** des doigts à capteur unique monte à l'approche, sans
contact. C'est la seule proximité exploitable ; les autres voies restent à zéro
tant que rien ne touche.

## Un actionneur mort

Cela se déclare **au lancement**, pas dans le code :

```bash
sudo python3 -m dh116.cli.pilote --exclure 1
```

Le moteur exclu n'est ni homé ni commandé. C'est important : le homing se fait
moteur par moteur justement parce qu'un actionneur défaillant ne termine jamais
le sien, le variateur finit par passer en alarme « hors position », et un
`home_motors(0)` global emporte alors toute la main.

