# Bootstrap du backend Terraform

À faire UNE SEULE FOIS, avant tout le reste.

```bash
cd infra/bootstrap
terraform init
terraform apply -var="state_bucket_name=eip-tfstate-CHANGE-ME-123"
```

Note le nom du bucket créé : tu le reporteras dans `infra/envs/dev/backend.tf`.
Ne mets JAMAIS le state de ce bootstrap sur le remote (poule & oeuf) — il reste local, commité gitignore.
