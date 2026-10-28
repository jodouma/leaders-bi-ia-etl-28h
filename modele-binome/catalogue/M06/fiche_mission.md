# Mission 06 — Hôtellerie — Dar Azur

**Client fictif :** Dar Azur (petit groupe de quatre maisons d'hôtes : Hammamet, Sidi Bou Saïd, Tozeur et Djerba). **Grain du fait :** un séjour (une réservation de chambre, de la date d'arrivée à la date de départ).
Données 100 % synthétiques : noms, chiffres et personnes sont inventés.

## Le contexte

Dar Azur exploite quatre maisons d'hôtes (64 chambres au total). Le logiciel de réception exporte les séjours dans un CSV, l'inventaire des chambres vit dans un classeur Excel, les contrats des canaux de vente (direct, agence en ligne, tour-opérateur, entreprise) et leurs commissions dans un fichier JSON, et les annulations et paiements dans une petite base SQLite. Le gérant voit des réservations partout, mais ne sait pas si ses chambres sont vraiment remplies ni ce qu'il reste après les annulations. Solen Digital vous confie la mission.

## Le message de la direction

> Bonjour à tous les deux,
> 
> Je veux savoir quelles maisons remplissent leurs chambres et lesquelles gagnent de l'argent. Par établissement et par mois : les nuitées vendues, le taux d'occupation, le revenu net d'annulations et le RevPAR. Je dois décider où mettre l'effort commercial cet hiver.
> 
> Pour information : à partir du 15 juillet, l'agence en ligne ne nous prend plus 18 % mais 15 % de commission. Les séjours arrivés avant cette date gardent 18 %.
> 
> Dites-moi aussi ce que vous avez dû écarter, et pourquoi.
> 
> Lamia Ben Salah, directrice (Solen Digital, pour le compte de Dar Azur)

## Ce que vous livrez

1. `outputs/rejets.csv` : chaque ligne écartée avec son motif.
2. `outputs/entrepot.sqlite` : une étoile (dim_date, dim_etablissement, dim_canal, fact_sejour, fact_annulation).
3. Le lot 2 chargé, l'historique gardé et un rejeu sans doublon. Le canal OTA (agence en ligne) passe d'une commission de 18 % à 15 % le 2026-07-15 (inclus). Cette information arrive avec `lot2/canaux.json`.
4. `outputs/export/*.csv` + `manifest.json`, puis le rapport Power BI actualisé.
5. `outputs/app/index.html` : une mini-application locale de trois écrans.
6. Une recommandation courte à la direction, appuyée sur les chiffres.

## Les indicateurs (définitions exactes)

- **Nuitées vendues** (nombre) : nuitées des séjours acceptés − nuitées des séjours annulés (annulations CONFIRMEE acceptées)
- **Taux d'occupation** (ratio) : nuitées vendues / (chambres × nuits de la période)
- **Revenu net d'annulations** (TND) : montant des séjours − remboursements
- **RevPAR** (TND) : revenu net / (chambres × nuits de la période), en TND par chambre disponible, arrondi au millime

Tous les montants sont stockés en **millimes entiers** (1 TND = 1 000 millimes) et affichés en TND à 3 décimales.

## Les données

- `lot1` (2026-01-01 → 2026-06-30) : chargement initial : séjours arrivés de janvier à juin 2026 (CSV en UTF-8)
- `lot2` (2026-07-01 → 2026-08-31) : incrément : arrivées de juillet-août ; recopie les séjours arrivés le 30 juin ; commission OTA 18 % → 15 % le 2026-07-15 ; **CSV encodé en cp1252**

Un `echantillon/` de 12 lignes permet de tout calculer à la main d'abord (voir `echantillon/attendu.md`).

## La règle à clarifier avec la direction

**Question :** Un client arrive le 30 juin et repart le 3 juillet (3 nuitées) : le séjour compte-t-il en juin, en juillet, ou nuit par nuit ? Et une réservation faite le 10 juillet sur l'agence en ligne pour une arrivée le 20 juillet : commission à 18 % (taux du jour de la réservation) ou 15 % (taux du jour d'arrivée) ?

- A : tout au mois d'arrivée ; commission au taux valable à la date d'arrivée.
- B : nuit par nuit (2 nuits en juin, 1 en juillet) ; il faut découper le montant.
- C : commission au taux valable à la date de réservation.

**Décision de la direction pour cette mission :** A. La date d'arrivée est la date du fait : nuitées, montant, commission (version du canal valable ce jour-là) et annulations éventuelles sont rangés dans le mois d'arrivée. Simple, stable et identique pour tous les établissements.

## Les trois écrans de l'application

1. **Vue direction** — nuitées vendues, taux d'occupation, revenu net d'annulations et RevPAR, puis le revenu net par mois et par établissement (barres empilées) ; filtres période et établissement.
2. **Détail par canal** — chaque canal avec ses versions : OTA à 18 % jusqu'au 2026-07-14, puis 15 % ; nuitées, revenu net et commissions par version.
3. **Qualité des données** — lignes lues, gardées, rejetées par motif et par lot ; annulations retirées ; séjours déjà chargés ignorés au lot 2.

## Trois variantes possibles (évolutions)

1. Nouvel indicateur : revenu net après commissions = revenu net d'annulations − commissions, par canal et par établissement.
2. Nouvelle règle : répartir les nuitées et le montant d'un séjour à cheval sur deux mois nuit par nuit (option B) — le fait passe au grain « nuitée » ; comparer le taux d'occupation de juin et juillet avec la règle actuelle.
3. Nouvelle source : charger la table `paiement` de `operations.sqlite` dans un `fact_paiement` et suivre le taux d'encaissement = paiements reçus / revenu net d'annulations.

## Comment savoir que c'est juste ?

```bash
python -m controles.verifier --mission M06 --etape tout
pytest controles
```

Les valeurs attendues sont dans `reference/attendu_lot1.json` et `reference/attendu_lot2.json`. Elles ont été calculées par le générateur depuis la vérité, pas par une solution.
