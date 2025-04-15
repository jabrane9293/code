# 🏎️ F1 Insights – Analyse & Prédictions 2024–2025

Ce projet a pour but d’analyser les performances des pilotes et des écuries de Formule 1 sur la période 2024–2025, à l’aide de visualisations et de modèles prédictifs en Python.

## 🎯 Objectifs

- Visualiser l’évolution des points obtenus par chaque pilote et chaque écurie depuis début 2024.
- Identifier les dynamiques ascendantes ou descendantes.
- Prédire les pilotes ayant le plus de chances d’atteindre le top 5 du prochain Grand Prix (Arabie Saoudite 2025).

## 🗂️ Structure du projet

f1-insights/ 
├── data/ │ ├── raw/ # Données brutes (CSV originaux) │ ├── processed/ # Données nettoyées et prêtes à l’analyse │ └── external/ # Autres sources externes (optionnel) 
├── notebooks/ # Analyses exploratoires, visualisations 
├── src/ │ ├── data/ # Scripts de traitement de données │ ├── viz/ # Fonctions de visualisation │ └── models/ # Modèles de prédiction 
├── outputs/ # Graphiques générés, prédictions, résultats 
├── requirements.txt # Liste des dépendances Python 
├── README.md # Ce fichier 
└── main.py # Script principal (optionnel)


## 📚 Librairies principales

- `pandas`, `numpy` : manipulation de données  
- `seaborn`, `matplotlib` : visualisations  
- `scikit-learn` : machine learning (RandomForestRegressor)  
- `jupyter` : notebooks interactifs

## 🚀 Lancer le projet

1. Cloner le dépôt :
```bash
git clone https://github.com/jaribou9293/f1-insights.git
cd f1-insights

