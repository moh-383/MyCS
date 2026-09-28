# MyCS

Assistant personnel de veille et de stratégie de carrière : recherche d'opportunités de stage, analyse de correspondance avec mon profil, et identification des compétences à renforcer.

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
careerscout/
├── profile.yaml          # profil personnel : formation, compétences, domaines, contraintes
├── src/
│   ├── search.py         # génération des requêtes + recherche web
│   ├── extract.py        # extraction structurée d'une offre
│   ├── match.py          # comparaison profil / offre
│   └── store.py          # stockage et déduplication
├── data/
│   └── opportunities.db  # base locale (SQLite)
├── docs/
│   └── cadrage.md        # document de cadrage du projet
└── README.md
```

## Profil

Le profil est décrit dans `profile.yaml` et sert de base à toutes les requêtes générées. Il inclut :
- formation et niveau ;
- compétences et niveau estimé ;
- domaines ciblés (avec pondération) ;
- pays et périodes de disponibilité ;
- contraintes (rémunération, mobilité, langues).

## Feuille de route

- [x] document de cadrage
- [ ] Profil V1 rempli
- [ ] Recherche + extraction sur un petit lot d'offres test
- [ ] Comparaison profil / offre (indispensable vs souhaité)
- [ ] Premier résumé automatique
- [ ] V2 : historique des candidatures, recommandations de formation
- [ ] V3 : préparation de candidature (avec validation humaine à chaque étape)

## Notes de décision

Les choix techniques et leurs raisons sont consignés au fil de l'eau dans `docs/decisions.md` (à créer), pour garder une trace de pourquoi telle source ou telle approche a été retenue ou abandonnée.

## Licence

Projet personnel, à but non commercial pour l'instant.
