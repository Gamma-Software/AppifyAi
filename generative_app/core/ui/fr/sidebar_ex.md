## Exemples Instructions

Donnez à AppifyAi les instructions suivantes :

Instructions simples :
- Ajoutez un titre avec le texte 'Hello World' et un sous-titre avec le texte 'Ceci est ma première application Streamlit'.
- Ajoutez une zone de texte avec le libellé 'Entrez votre nom' et une autre avec le libellé 'Entrez votre âge' et un bouton avec le libellé 'Soumettre'. Lorsque vous cliquez sur le bouton, affichez le texte 'Bonjour, <nom> ! Vous avez <âge> ans.
- Ajoutez une barre latérale à l'application avec un menu déroulant pour sélectionner des options ("mettre à jour", "enregistrer", "réinitialiser").

Télécharger des fichiers et afficher des graphiques :
- Afficher la fonction f(x) = x^2 dans un graphique linéaire pour x dans [-10, 10] et donner un nom adéquat au graphique.
- Donner la possibilité de télécharger un fichier csv et d'afficher son contenu dans un tableau après le téléchargement.
- Donner la possibilité de télécharger un fichier csv et d'afficher un diagramme à barres montrant les données.
- Donner la possibilité de télécharger un fichier csv et de stocker les données dans un cadre de données pandas pour afficher ultérieurement des statistiques, puis créer une boîte de sélection pour sélectionner la colonne dans laquelle les statistiques seront affichées. Soyez créatif et affichez les statistiques que vous voulez

Applications utiles :
- Demande d'entrer une première date et une deuxième date et d'afficher le nombre de jours qui les séparent. Ajoutez un titre et un texte explicatif en conséquence avant la saisie de la date.
- Demandez d'entrer une première date et une deuxième date et affichez le nombre de jours ouvrables qui les séparent. Ajoutez un titre et un texte explicatif avant la saisie de la date. Soyez créatif avec le texte d'explication et ajoutez des emojis.
- créer une application qui détecte les visages
- créer une application qui calcule l'IMC à partir d'un poids et d'une taille, puis ajouter une boîte de sélection pour choisir l'unité du poids et de la taille (kg, lbs, cm, inch), puis ajouter un texte expliquant l'IMC et ce qu'il signifie, puis ajouter la formule en latex et enfin ajouter un graphique qui affiche l'IMC de l'utilisateur et l'IMC moyen de la population.
- créer une application qui calcule la similarité entre deux images
- créer une application qui lit les codes barres

Webscraping :
- Webscraping de ce site (https://fr.wikipedia.org/wiki/Blog) et affichage de toutes les classes 'mw-headline'.

Création de jeux :
- Créez-moi un jeu de dés

Utilisation d'API ouvertes :
- Afficher des photos de chats au hasard en utilisant des API ouvertes et ajouter un bouton pour mettre à jour l'image.

Instructions plus complexes :
- stocker les valeurs csv de cette url : "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/exports/csv?limit=-1&timezone=UTC&use_labels=false&epsg=4326" dans un dataframe pandas (et le mettre en cache). utiliser le délimiteur " ;". Nettoyer les données en appliquant une division de 100000 à la colonne latitude et longitude et en supprimant toutes les données None dans la colonne "gazole_prix" et en supprimant tous les "gazole_prix" supérieurs à 3. Ajoutez un graphique plotly avec la librairie streamlit qui affiche une carte ouverte avec les coordonnées des colonnes "latitude" et "longitude" du dataframe et étiquettez-les avec la colonne "gazole_prix". Utilisez également "gazole_prix" pour colorer et dimensionner les marqueurs. La gamme de couleurs des marqueurs doit correspondre aux valeurs minimale et maximale de la colonne. Créez une nouvelle colonne de taille égale à 1/("gazole_prix")^4 ; ainsi, plus la gazole est chère, plus le marqueur est petit.