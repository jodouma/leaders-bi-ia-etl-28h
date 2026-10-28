# Mission 08 — Maintenance · TechniServ

**Client fictif :** TechniServ (maintenance sous contrat de climatisations, ascenseurs et groupes électrogènes). **Grain du fait :** une intervention d'un technicien sur un équipement.
Données 100 % synthétiques : noms, chiffres et personnes sont inventés.

## Le contexte

TechniServ entretient et dépanne 48 équipements (climatisations, ascenseurs, groupes électrogènes) chez 9 clients, avec 10 contrats de maintenance payés au mois. Les techniciens saisissent chaque intervention dans un export CSV ; le catalogue des pièces et les taux horaires sont dans un classeur Excel ; le parc d'équipements (site, catégorie, contrat) est dans un fichier JSON ; les contrats et les pièces consommées sont dans la base SQLite de l'atelier. Personne ne sait dire quels contrats rapportent vraiment, une fois payés les techniciens et les pièces. Solen Digital vous confie la mission.

## Le message de la direction

> Bonjour à tous les deux,
> 
> Nos contrats de maintenance sont-ils rentables ? Je veux, par contrat, par équipement, par catégorie et par mois : le nombre d'interventions, le délai moyen d'intervention sur les pannes, le coût d'intervention (pièces + main-d'œuvre) et la marge de service. Je veux savoir quels contrats et quels équipements mobilisent le plus nos équipes. Dites-moi aussi ce que vous avez dû écarter, et pourquoi.
> 
> Pour information : le 15 juillet, le groupe électrogène EQ-017 du Groupe Nakhla passe du contrat standard CT-03 au contrat premium CT-09. Ses interventions d'avant doivent rester sur CT-03.
> 
> Lamia Ben Salah, directrice (Solen Digital, pour le compte de TechniServ)

## Ce que vous livrez

1. `outputs/rejets.csv` : chaque ligne écartée avec son motif.
2. `outputs/entrepot.sqlite` : une étoile (dim_date, dim_contrat, dim_equipement, fact_intervention, fact_revenu_contrat).
3. Le lot 2 chargé, l'historique gardé et un rejeu sans doublon. L'équipement EQ-017 (groupe électrogène du Groupe Nakhla) passe du contrat « CT-03 » au contrat « CT-09 » le 2026-07-15 (inclus). Cette information arrive avec `lot2/equipements.json`.
4. `outputs/export/*.csv` + `manifest.json`, puis le rapport Power BI actualisé.
5. `outputs/app/index.html` : une mini-application locale de trois écrans.
6. Une recommandation courte à la direction, appuyée sur les chiffres.

## Les indicateurs (définitions exactes)

- **Interventions** (nombre) : nombre d'interventions acceptées (préventives + correctives)
- **Délai moyen d'intervention** (heures, nombre décimal) : somme des délais des interventions correctives / nombre d'interventions correctives ; délai = (date + heure d'intervention) − (date + heure de demande), en heures ; le préventif est exclu ; résultat en heures décimales (ex. 20,18 h)
- **Coût d'intervention** (TND) : coût des pièces + coût de main-d'œuvre
- **Marge de service** (TND) : revenu de contrat − coût d'intervention ; marge PARTIELLE (ni déplacements, ni frais de structure) ; à lire par contrat, par mois ou au total

Tous les montants sont stockés en **millimes entiers** (1 TND = 1 000 millimes) et affichés en TND à 3 décimales.

## Les données

- `lot1` (2026-01-01 → 2026-06-30) : chargement initial, janvier → juin 2026
- `lot2` (2026-07-01 → 2026-08-31) : incrément juillet → août 2026 ; recopie les interventions du 30 juin ; EQ-017 passe du contrat CT-03 au contrat CT-09 le 2026-07-15

Un `echantillon/` de 12 lignes permet de tout calculer à la main d'abord (voir `echantillon/attendu.md`).

## La règle à clarifier avec la direction

**Question :** (1) EQ-017 tombe en panne le 14 juillet à 19 h (contrat CT-03) ; le technicien intervient le 15 juillet à 9 h, jour où EQ-017 passe sur CT-09. Quel contrat paie cette intervention ? (2) Une visite préventive est planifiée trois semaines à l'avance : quel est son « délai » ?

- (1) A : contrat valable à la date de la demande (CT-03).
- (1) B : contrat valable à la date d'intervention (CT-09).
- (2) A : délai = intervention − planification, compté dans le délai moyen.
- (2) B : délai calculé et stocké, mais le préventif est exclu du délai moyen.

**Décision de la direction pour cette mission :** (1) B : chaque intervention est rattachée à la version de l'équipement valable à sa DATE D'INTERVENTION (la date du fait, `date_key`) ; c'est ce jour-là que le travail et les pièces sont consommés. (2) B : `delai_heures` est stocké pour toutes les interventions, mais le délai moyen ne compte que les correctives (la « demande » d'un préventif est une date de planification, pas une panne).

## Les trois écrans de l'application

1. **Vue direction** — interventions, délai moyen (correctifs), coût d'intervention, revenu et marge de service ; coût d'intervention par mois et par catégorie (barres empilées) ; filtres période et contrat.
2. **Détail par équipement** — chaque équipement avec ses versions de contrat : EQ-017 sur CT-03 jusqu'au 2026-07-14, puis CT-09 ; ses interventions et son coût par contrat et par mois.
3. **Qualité des données** — lignes lues, gardées, déjà chargées, rejetées par motif, par source et par lot.

## Trois variantes possibles (évolutions)

1. Nouvel indicateur : taux de respect du délai garanti = correctifs avec `delai_heures` ≤ délai garanti du contrat (nouvelle colonne `delai_garanti_heures` dans `contrat`) / correctifs.
2. Nouvelle règle : une intervention de plus de 8 heures facturées doit être validée par le chef d'atelier ; sans validation, elle est rejetée avec un nouveau motif `heures_hors_plafond`.
3. Changement historique : l'ascenseur EQ-014 passe au contrat CT-09 le 2026-08-01 (deuxième équipement historisé ; ses interventions de juillet restent sur CT-03).

## Comment savoir que c'est juste ?

```bash
python -m controles.verifier --mission M08 --etape tout
pytest controles
```

Les valeurs attendues sont dans `reference/attendu_lot1.json` et `reference/attendu_lot2.json`. Elles ont été calculées par le générateur depuis la vérité, pas par une solution.
