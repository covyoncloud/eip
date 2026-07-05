# ADR-001 : Architecture fondatrice de l'Entity Intelligence Platform (EIP)

- **Statut** : accepté
- **Date** : 2026-07-04

## Contexte

EIP est une plateforme cloud-native (AWS) qui ingère des données d'**œuvres musicales** depuis des sources hétérogènes, les normalise vers un format canonique, déduplique et réconcilie les entités (y compris via IA), puis expose le référentiel propre via API, analytique et assistant conversationnel.

Objectifs du projet :
1. Support d'apprentissage sur 6 mois pour monter en compétence AWS (Developer → fondations Architect).
2. Actif portfolio démontrable pour un positionnement freelance AWS.
3. Rejouer un problème réel connu (normalisation multi-sources, façon plateforme Qirin/Allianz), donc crédible en entretien.

Contraintes :
- Budget perso strict (< 50 €/mois).
- Sources de données gratuites obligatoires.
- Travail en autonomie, piloté par objectifs.

## Décision

### D1 — Domaine : œuvres musicales
Retenu pour la richesse des données ouvertes gratuites et la narration (lien Sacem/musique). L'entité centrale est l'**œuvre** (composition), pas l'enregistrement.

### D2 — Trois sources hétérogènes
| Source | Accès | Rôle | Format |
|--------|-------|------|--------|
| **MusicBrainz** | Dump PostgreSQL complet (gratuit) + API 1 req/s | Source pivot de référence | relationnel → export |
| **Discogs** | API gratuite (token) | Source secondaire, modèle différent | JSON |
| **Fichiers legacy "sales"** | générés à la main (CSV/XML) | Simule un provider legacy, variations et doublons volontaires | CSV/XML |

Le cœur du problème est de faire matcher la **même œuvre** à travers ces trois représentations divergentes (ex : `Beyoncé — Crazy in Love` / `BEYONCE Crazy In Love feat JAY Z` / `crazy in love (beyonce ft. jay-z)`).

**Stratégie d'accès MusicBrainz** : ingestion en masse depuis le **dump** (pas de rate limit), pas requête par requête. L'API n'est utilisée que pour simuler une source "temps réel" au Sprint 2, avec throttling à 1 req/s et User-Agent explicite (obligatoire, sinon blocage IP).

### D3 — Modèle pivot canonique : `CanonicalWork`
Champs : `work_id` (UUID interne), `title_normalized` / `title_raw`, `artists[]`, `iswc` (nullable), `identifiers{}` (source → id externe), `isrcs[]`, `language`, `first_release_year`, `genres[]`, `source_records[]` (provenance), `confidence_score`, timestamps.

**Clé de dédup métier** : priorité à l'ISWC s'il existe, sinon `hash(titre_normalisé + artiste_principal)`. Cette clé alimente l'index DynamoDB (Sprint 2).

### D4 — Choix d'architecture
- **Serverless-first** (Lambda, Step Functions, API Gateway) — cœur du profil AWS Developer, scale à zéro, pricing à l'usage.
- **Langage : Python** (FastAPI côté service, Boto3 côté AWS) — langage naturel de l'écosystème.
- **Architecture hexagonale** — domaine isolé, testable sans infra ; ports & adapters.
- **Data lake medallion S3** (bronze/silver/gold) + **DynamoDB** (lookup/dédup) + **Aurora PostgreSQL Serverless v2** (canonique + pgvector RAG).
- **IaC : Terraform** — state remote S3 + lock DynamoDB, multi-comptes via `assume_role` (à partir du Sprint 5).
- **IA : Bedrock** — entity resolution + RAG, sans entraîner de modèle.

### D5 — Licences (gouvernance des données)
- **MusicBrainz** : données core sous **CC0** (domaine public) ; certaines annotations sous CC BY-NC-SA. Usage non-commercial du web service gratuit.
- **Discogs** : données sous leurs conditions d'API ; usage non-commercial respecté.
- **Fichiers legacy** : générés par nos soins, aucune contrainte.
- **Décision** : usage strictement **non-commercial** (portfolio). Toute source et sa licence sont documentées. Aucune redistribution de données brutes de tiers dans le repo public — seuls des échantillons synthétiques y figurent.

## Alternatives considérées

- **Domaine "entreprises"** (façon Qirin) : écarté au profit des œuvres pour la richesse open data et la narration, mais reste un pivot mental valide.
- **Java/Spring** : écarté — objectif explicite de bascule vers Python/serverless.
- **Tout relationnel (Aurora seul)** : écarté — le lookup massif par clé métier justifie DynamoDB à côté.
- **Fine-tuning d'un modèle** pour la réconciliation : écarté — le RAG + prompt engineering suffit, moins cher, plus maintenable.

## Conséquences

**Positives** : couverture large des services AWS et des 6 piliers Well-Architected ; problème de réconciliation authentique ; zéro coût de données ; narration crédible.

**Négatives / dette assumée** : le dump MusicBrainz est volumineux (plusieurs Go) → l'ingestion batch doit être pensée dès le Sprint 2 (Glue). Le rate limit API impose une discipline de throttling. Multi-comptes ajoute de la complexité, repoussée au Sprint 5.

**Implications** : le Sprint 1 se concentre sur la chaîne CSV/JSON/XML → pivot → Aurora, en local puis sur AWS. Le dump MusicBrainz complet arrive au Sprint 2 avec Glue.
