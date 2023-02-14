# Présentation
Le but de l'exercice est d'écrire une version béta d'un script destiné à extraire et convertir les informations de reventes des produits proposé par diverses librairies en ligne. Le site utilisé pour l'exercice est "http://books.toscrape.com/" (fictif). 

# Fonctionnement 
Le script se connecte à l'URL principale du site, créer un objet python "OnlineLibrary" et extrait les URLs des différentes catégories de livres.

Ensuite, chaque page de catégories est visitée afin d'en faire un objet python "Category" avant d'extraire les URLs des livres de cette catégorie.

Une fois les URLs individuels extrait, chaque page est visitée afin de convertir les informations présentes sur les URLs de chaque livre en un objet python "Book". 

Les informations extraites sont alors sauvegardées au format CSV (Détails des livres) et JPG (Couverture des livres).

# Utilisation
## 1) Creer l'environnement virtuel
Ouvrez un terminal; 

Pour ouvrir un terminal sur Windows, pressez  touche windows + r et entrez cmd.

Sur Mac, pressez touche command + espace et entrez "terminal".

Sur Linux, vous pouvez ouvrir un terminal en pressant les touches Ctrl + Alt + T.

Placez-vous dans le dossier où vous souhaitez créer l'environnement (Pour plus de facilité aux étapes suivantes, il est recommandé de faire cette opération dans le dossier contenant le script à exécuté). Puis exécutez  à présent la commande : 

`python -m venv env
`

Une fois fait, un nouveau dossier "env" devrait être créé dans le répertoire, il s'agit de votre environnement virtuel.

## 2) Activer l'environnement virtuel

Une fois la première étape réalisée, vous pouvez à présent activer votre environnement.
Pour ce faire, dans le dossier ou l'environnement a été créé :


Ouvrez un terminal, rendez-vous au chemin d'installation de votre environnement puis exécutez la commande : 

- Windows (Cmd) : `env\Scripts\activate.bat`
- bash/zsh : `source venv/bin/activate`
- fish : `source venv/bin/activate.fish`
- csh/tcsh : `source venv/bin/activate.csh`
- PowerShell : `venv/bin/Activate.ps1`

Une fois fait, vous constatez que les lignes de votre cmd commencent à présent par "(env)", cela signifie que votre environnement est actif.

## 3) Installer les dépendances

Dans le même terminal qu'à l'étape précédente :

`pip install -r requirements.txt`

## 4) Executer le programme
Lors du premier lancement du script, il est important de suivre les étapes l'une après l'autre. Lors des exécutions suivantes, il est possible de réutiliser l'environnement créer précédemment. Pour ce faire, ne suivez que l'étape 2 (Activer l'environnement virtuel), vous pouvez alors simplement contrôler que les dépendances sont bien installées via la commande : `pip freeze`. Si toutes les dépendances sont bien présentes, il est possible de passer directement à l'exécution du script.

Dans le terminal ayant servi à l'activation de l'environnement virtuel, exécuter la commande : 

`python scrape.py`

# Output
Une fois l'exécution du script terminée, les informations recueillies sont sauvegardées dans un dossier propre à chaque site de revendeur visité (uniquement http://books.toscrape.com/ dans l'état, enregistrer dans le dossier : "BookToScrape").

Ce dossier est organisé de façon à obtenir : 

* Un fichier csv par catégories, contenant les informations de chacun des livres présent dans la catégorie.
* Un dossier "book_cover" comprenant un sous dossier par catégories, reprennant les images de couvertures de chacun des livres présents dans cette catégorie.
