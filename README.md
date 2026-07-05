# EIP — Entity Intelligence Platform

Plateforme cloud-native (AWS) d'ingestion, normalisation et réconciliation d'**œuvres musicales** depuis des sources hétérogènes, avec enrichissement IA (Bedrock). Projet portfolio — voir [ADR-001](docs/adr/001-architecture.md) pour les décisions fondatrices.

## Objectif du projet

Monter en compétence AWS (Developer → fondations Architect) sur 6 mois, piloté par objectifs, et produire un actif portfolio freelance. Le problème rejoue une plateforme de normalisation multi-sources façon Qirin/Allianz.

## Architecture (cible)

```
Sources (MusicBrainz dump / Discogs API / fichiers legacy)
   -> Ingestion (API Gateway + Lambda / S3)
   -> S3 bronze -> SQS -> Normalisation -> S3 silver
   -> Dédup (DynamoDB) + Réconciliation IA (Bedrock)
   -> Aurora PostgreSQL (canonique) -> S3 gold
   -> Serving : API REST + Athena + Assistant RAG
Transverse : Terraform (IaC) • CI/CD • Cognito/IAM/KMS • CloudWatch/X-Ray • FinOps
```

Détail complet dans l'ADR-001 et le plan de projet 6 mois.

## Structure du repo

```
eip/
├── docs/adr/            # Architecture Decision Records (commence par 001)
├── infra/
│   ├── bootstrap/       # crée le backend Terraform (S3 state + DynamoDB lock) — 1 seule fois
│   ├── modules/         # network / storage / compute (à remplir au fil des sprints)
│   └── envs/dev/        # environnement dev (référence le backend remote)
├── services/
│   └── ingestion/       # service FastAPI (architecture hexagonale)
│       └── src/ingestion/
│           ├── domain/        # CanonicalWork (pivot) — zéro dépendance externe
│           ├── application/    # ports (interfaces) + use cases
│           └── adapters/       # parsers CSV/JSON/XML + repository
├── .github/workflows/   # CI (lint + test + terraform validate)
├── docker-compose.yml   # stack locale (API + PostgreSQL)
└── Makefile             # raccourcis (make test / run / up / bootstrap / plan)
```

## Démarrage rapide (local, sans AWS)

```bash
make install        # installe le service
make test           # lance les tests (health + business_key passent déjà)
make run            # API sur http://localhost:8080  (/health, /docs)
# ou :
make up             # stack complète docker-compose (API + PostgreSQL)
```

## Mise en place du backend Terraform (avant tout déploiement AWS)

```bash
# 1. Bootstrap (une seule fois) — crée le bucket S3 de state + table de lock
cd infra/bootstrap
terraform init
terraform apply -var="state_bucket_name=eip-tfstate-CHANGE-ME-123"

# 2. Reporte le nom du bucket dans infra/envs/dev/backend.tf
# 3. Puis :
cd ../envs/dev
terraform init
terraform plan
```

## Où j'en suis / feuille de route

Suivi par **sprints pilotés par objectifs** (voir le plan de projet 6 mois). État actuel :

- [x] Sprint 0 — squelette repo, ADR-001, backend remote Terraform
- [ ] **Sprint 1** — chaîne CSV/JSON/XML → pivot → Aurora, déployée sur AWS via Terraform
- [ ] Sprint 2 — pipeline event-driven (SQS, Step Functions, Glue) + dump MusicBrainz
- [ ] Sprint 3 — réconciliation Bedrock + assistant RAG
- [ ] Sprint 4 — serving (API, Athena, Cognito, WAF)
- [ ] Sprint 5 — multi-comptes, CI/CD complet, EKS, observabilité
- [ ] Sprint 6 — durcissement Well-Architected + finalisation portfolio

## Prochaines actions (Sprint 1)

1. Implémenter les 3 parsers (`adapters/parsers.py`) + la normalisation (`_normalize`).
2. Modèle SQLAlchemy + migration Alembic, brancher `SqlAlchemyWorkRepository`.
3. Faire passer un vrai `/ingest` de bout en bout en local (`make up`).
4. Écrire le module Terraform `storage` (S3 + Aurora) puis `compute` (ECR + Fargate + ALB).
5. Déployer sur AWS, `curl` l'ALB.

Chaque brique a un `TODO(Sprint X)` dans le code pour te guider sans te tenir la main.
