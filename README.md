# MyCS

Assistant personnel de veille et de stratégie de carrière : recherche d'opportunités de stage, analyse de correspondance avec mon profil, et identification des compétences à renforcer.

L'objectif n'est pas simplement de trouver des offres correspondant à mes compétences actuelles , mais également d'identifier les opportunités susceptibles de contribuer à ma **trajectoire professionnelle à long terme**.

> Statut : en construction : V1 (Scout)

## Pourquoi ce projet

Trouver des offres de stage pertinentes (data science, statistiques, scoring, robotique/automatisation) demande de surveiller beaucoup de sources différentes, et de comparer chaque offre à son propre profil pour savoir si elle vaut le coup. CareerScout automatise cette veille et cette comparaison, en gardant l'utilisateur seul décideur pour toute candidature.

## Objectif de la V1

Recevoir régulièrement une sélection d'opportunités (stages, programmes de recherche) correspondant à un profil défini, avec pour chacune :
- un niveau de correspondance ;
- les compétences déjà couvertes et celles qui manquent ;
- une explication du pourquoi.

Pas de candidature automatique à ce stade : le système informe, il ne postule pas.

### Hors périmètre (V1)

- Candidature automatique ou génération de CV/lettre de motivation
- Interface web ou tableau de bord
- Automatisation via des outils tiers (n8n ou équivalent)
- Support multi-utilisateur

## Fonctionnement (V1)

```
Profil (fichier de config)
        │
        ▼
Génération de requêtes de recherche
        │
        ▼
Recherche web
        │
        ▼
Extraction structurée par offre (compétences, domaine, date limite...)
        │
        ▼
Déduplication + stockage
        │
        ▼
Comparaison avec le profil (indispensable / souhaité)
        │
        ▼
Résumé périodique (les meilleures offres + lacunes récurrentes)
```

## Structure du dépôt

```
MyCS/
│
├── profile.yaml              # Tes données personnelles
├── profile_schema.yaml       # Contrat/validation de profile.yaml
│
├── src/
│   ├── __init__.py
│   ├── config.py             # Configuration générale
│   ├── validate.py           # Validation du profil
│   ├── search.py             # Génération des requêtes + recherche
│   ├── extract.py            # Extraction structurée d'une offre
│   ├── match.py              # Profil ↔ opportunité
│   └── store.py              # SQLite + stockage + déduplication
│
├── data/
│   └── opportunities.db      # Base locale SQLite
│
├── docs/
│   └── MyCS_Cahier_des_charges_technique_V1.pdf            # Cadrage du projet
│
├── tests/
│   ├── test_validate.py
│   ├── test_match.py
│   └── test_store.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

## Profil

Le profil est décrit dans `profile.yaml` et sert de base à toutes les requêtes générées. Il inclut :
- formation et niveau ;
- compétences et niveau estimé ;
- domaines ciblés (avec pondération) ;
- pays et périodes de disponibilité ;
- contraintes (rémunération, mobilité, langues).

### `profile_schema.yaml`

Définit la structure que `profile.yaml` doit respecter.

Il permet notamment de vérifier :

* les champs obligatoires ;
* les types de données ;
* les valeurs autorisées ;
* les plages de valeurs ;
* la structure générale du profil.

Il constitue le **contrat de données** de CareerScout.

### `src/validate.py`

Valide `profile.yaml` à partir de `profile_schema.yaml`.

Objectif :

```text
profile.yaml
     ↓
Validation
     ↓
✓ Profil valide
```

ou :

```text
profile.yaml
     ↓
Validation
     ↓
✗ Erreurs de structure
```

### `src/search.py`

Responsable de la génération de requêtes et de la recherche d'opportunités.

Les recherches doivent être générées à partir du profil plutôt que d'être entièrement codées en dur.

### `src/extract.py`

Transforme une page ou une source d'opportunité en données structurées.

Exemple :

```text
Page Web
   ↓
Extraction
   ↓
Opportunity
```

Informations potentielles :

* titre ;
* organisation ;
* localisation ;
* type ;
* période ;
* durée ;
* deadline ;
* niveau académique ;
* compétences ;
* financement ;
* mode de travail ;
* URL ;
* description.

Une information absente ou incertaine ne doit pas être inventée.

### `src/match.py`

Compare une opportunité au profil.

Le moteur doit progressivement distinguer :

* **Match Score** : adéquation avec les compétences actuelles ;
* **Trajectory Score** : contribution à la trajectoire professionnelle ;
* **Constraint Fit** : compatibilité avec les contraintes ;
* **Skill Gaps** : compétences manquantes.

### `src/store.py`

Responsable du stockage local des opportunités dans SQLite.

Il gère notamment :

* insertion ;
* récupération ;
* mise à jour ;
* déduplication ;
* identification des opportunités déjà analysées.

### `data/opportunities.db`

Base de données SQLite locale contenant les opportunités collectées et leurs informations associées.

La base est générée localement et ne doit pas nécessairement être versionnée dans Git.

## Feuille de route

- [x] document de cadrage
- [ ] Profil V1 rempli
- [ ] Recherche + extraction sur un petit lot d'offres test
- [ ] Comparaison profil / offre (indispensable vs souhaité)
- [ ] Premier résumé automatique
- [ ] V2 : historique des candidatures, recommandations de formation
- [ ] V3 : préparation de candidature (avec validation humaine à chaque étape)

## Exécuter la V1

Créer un environnement virtuel, installer les dépendances, puis valider le profil :

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m src.validate
.\.venv\Scripts\python -m pytest -q
```

Les modules V1 sont volontairement déterministes : `src.search.generate_queries()` produit les requêtes,
`src.extract.normalize_opportunity()` normalise une offre, `src.match.evaluate_opportunity()` retourne les
trois scores et les lacunes, et `src.store.OpportunityStore` persiste les offres dans SQLite.

## Notes de décision

Les choix techniques et leurs raisons sont consignés au fil de l'eau dans `docs/decisions.md` (à créer), pour garder une trace de pourquoi telle source ou telle approche a été retenue ou abandonnée.

## Licence

Projet personnel, à but non commercial pour l'instant.
