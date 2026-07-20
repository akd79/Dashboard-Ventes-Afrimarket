"""
Data cleaning - AfriMarket
Transforme data/afrimarket_dataset_senior.csv (brut) en data/df_clean.csv
"""
import pandas as pd
import numpy as np

RAW_PATH = "data/afrimarket_dataset_senior.csv"
CLEAN_PATH = "data/df_clean.csv"
REPORT_PATH = "rapport/audit_report.txt"

report_lines = []


def log(msg=""):
    report_lines.append(str(msg))


df = pd.read_csv(RAW_PATH)
n_raw = len(df)
log("=== AUDIT & NETTOYAGE - AfriMarket ===")
log(f"Lignes brutes : {n_raw}")
log(f"Colonnes : {list(df.columns)}")
log()

# ------------------------------------------------------------------
# 1. Doublons exacts (100 lignes id_commande + toutes colonnes identiques)
# ------------------------------------------------------------------
n_dup = df.duplicated().sum()
df = df.drop_duplicates(keep="first").reset_index(drop=True)
log(f"[Doublons] {n_dup} lignes strictement dupliquees supprimees -> {len(df)} lignes restantes")

# ------------------------------------------------------------------
# 2. Dates : deja au format ISO YYYY-MM-DD, on force le dtype datetime
# ------------------------------------------------------------------
df["date_commande"] = pd.to_datetime(df["date_commande"], errors="coerce")
n_bad_dates = df["date_commande"].isna().sum()
log(f"[Dates] {n_bad_dates} dates non convertibles (attendu 0)")

# ------------------------------------------------------------------
# 3. Villes mal orthographiees : Kinshassa -> Kinshasa
# ------------------------------------------------------------------
n_ville_fix = (df["ville"] == "Kinshassa").sum()
df["ville"] = df["ville"].replace({"Kinshassa": "Kinshasa"})
log(f"[Villes] {n_ville_fix} lignes 'Kinshassa' corrigees en 'Kinshasa'")
log(f"  Villes finales : {sorted(df['ville'].unique())}")

# ------------------------------------------------------------------
# 4. Categorie : la colonne brute est corrompue (valeur 'electronique'
#    minuscule melange des produits des 4 vraies categories).
#    Le prefixe de nom_produit ('Produit_<Categorie>_NN') est fiable
#    a 100% (verifie : 0 produit avec prefixe incoherent).
#    -> categorie reconstruite depuis nom_produit.
# ------------------------------------------------------------------
prefix = df["nom_produit"].str.extract(r"^Produit_([^_]+)_")[0]
n_incoherent_before = (df["categorie"].str.lower() != prefix.str.lower()).sum()
df["categorie"] = prefix
log(f"[Categorie] colonne reconstruite depuis nom_produit (prefixe 100% fiable)")
log(f"  {n_incoherent_before} lignes avaient une categorie brute incoherente / mal casee")
log(f"  Categories finales : {sorted(df['categorie'].unique())}")

# ------------------------------------------------------------------
# 5. Statuts : casse non uniforme (Livree / retournee / Annulee)
# ------------------------------------------------------------------
statut_map = {
    "Livrée": "Livrée",
    "livrée": "Livrée",
    "retournée": "Retournée",
    "Retournée": "Retournée",
    "Annulée": "Annulée",
    "annulée": "Annulée",
}
df["statut_commande"] = df["statut_commande"].str.strip().replace(statut_map)
df["statut_commande"] = df["statut_commande"].str.capitalize()
log(f"[Statuts] casse uniformisee : {sorted(df['statut_commande'].unique())}")
log(df["statut_commande"].value_counts().to_string())
log()

# ------------------------------------------------------------------
# 6. Prix unitaire aberrant
#    - valeur sentinelle -50.00 (610 lignes) = marqueur de prix manquant
#      -> impute par la mediane du meme produit (nom_produit)
#    - autres valeurs negatives isolees (~22 lignes) = erreur de signe
#      -> valeur absolue
# ------------------------------------------------------------------
n_sentinel = (df["prix_unitaire"] == -50.00).sum()
n_other_neg = ((df["prix_unitaire"] < 0) & (df["prix_unitaire"] != -50.00)).sum()

df.loc[(df["prix_unitaire"] < 0) & (df["prix_unitaire"] != -50.00), "prix_unitaire"] = df.loc[
    (df["prix_unitaire"] < 0) & (df["prix_unitaire"] != -50.00), "prix_unitaire"
].abs()

median_price_by_product = df.loc[df["prix_unitaire"] > 0].groupby("nom_produit")["prix_unitaire"].median()
mask_sentinel = df["prix_unitaire"] == -50.00
df.loc[mask_sentinel, "prix_unitaire"] = df.loc[mask_sentinel, "nom_produit"].map(median_price_by_product)

log(f"[Prix] {n_sentinel} valeurs sentinelles (-50.00) imputees par la mediane du produit")
log(f"[Prix] {n_other_neg} valeurs negatives isolees corrigees (valeur absolue)")
log(f"  Prix <= 0 restants : {(df['prix_unitaire'] <= 0).sum()}")

# ------------------------------------------------------------------
# 7. Remise negative : sentinelle unique -0.10 (614 lignes) -> erreur de
#    signe, la distribution normale va de 0 a 0.30 -> valeur absolue
# ------------------------------------------------------------------
n_remise_neg = (df["remise"] < 0).sum()
df["remise"] = df["remise"].abs()
log(f"[Remise] {n_remise_neg} valeurs negatives (-0.10) corrigees (valeur absolue)")
log(f"  Remise range apres correction : [{df['remise'].min()}, {df['remise'].max()}]")

# ------------------------------------------------------------------
# 8. Quantite nulle (608 lignes) : aucune quantite livree/retournee ne
#    peut valoir 0 -> incoherence de saisie -> lignes supprimees
#    (impossible de calculer un CA/marge fiable pour ces commandes)
# ------------------------------------------------------------------
n_qty_zero = (df["quantite"] == 0).sum()
df = df[df["quantite"] > 0].reset_index(drop=True)
log(f"[Quantite] {n_qty_zero} lignes avec quantite=0 supprimees (incoherentes)")

log()
log(f"Lignes finales apres nettoyage : {len(df)} (perte totale : {n_raw - len(df)} lignes, "
    f"{100*(n_raw-len(df))/n_raw:.1f}%)")

df.to_csv(CLEAN_PATH, index=False)
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print("OK - df_clean genere :", len(df), "lignes")
