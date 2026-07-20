"""
Calcule tous les KPI demandes et les serialise dans data/kpis.json
(source unique de verite reutilisee par le notebook, le dashboard et le
resume executif).
"""
import json
import pandas as pd
import numpy as np

df = pd.read_csv("data/df_features.csv", parse_dates=["date_commande"])

kpis = {}

# ------------------------------------------------------------------
# 4.1 Performance globale
# ------------------------------------------------------------------
ca_total = df.loc[df["statut_commande"] != "Annulée", "chiffre_affaires"].sum()
profit_net_total = df["profit_net"].sum()
panier_moyen = df.loc[df["statut_commande"] != "Annulée", "chiffre_affaires"].pipe(
    lambda s: s.sum() / (df["statut_commande"] != "Annulée").sum()
)
taux_annulation = (df["statut_commande"] == "Annulée").mean()
taux_retour = (df["statut_commande"] == "Retournée").mean()
nb_commandes = len(df)

kpis["performance_globale"] = {
    "ca_total": round(ca_total, 2),
    "profit_net_total": round(profit_net_total, 2),
    "panier_moyen": round(panier_moyen, 2),
    "taux_annulation": round(taux_annulation * 100, 2),
    "taux_retour": round(taux_retour * 100, 2),
    "nb_commandes": int(nb_commandes),
}

# ------------------------------------------------------------------
# 4.2 Analyse par categorie
# ------------------------------------------------------------------
cat = df.groupby("categorie").agg(
    ca=("chiffre_affaires", lambda s: s[df.loc[s.index, "statut_commande"] != "Annulée"].sum()),
    marge=("marge_brute", lambda s: s[df.loc[s.index, "statut_commande"] != "Annulée"].sum()),
    profit_net=("profit_net", "sum"),
    nb_commandes=("id_commande", "count"),
    taux_retour=("indicateur_retour", "mean"),
).reset_index()
cat["taux_retour"] = (cat["taux_retour"] * 100).round(2)
cat = cat.sort_values("ca", ascending=False)

evo_mensuelle_cat = (
    df[df["statut_commande"] != "Annulée"]
    .groupby(["mois", "categorie"])["chiffre_affaires"].sum()
    .reset_index()
)

kpis["categorie"] = {
    "table": cat.round(2).to_dict(orient="records"),
    "categorie_prioritaire_ca": cat.iloc[0]["categorie"],
    "categorie_pire_retour": cat.sort_values("taux_retour", ascending=False).iloc[0]["categorie"],
    "evolution_mensuelle": evo_mensuelle_cat.round(2).to_dict(orient="records"),
}

# ------------------------------------------------------------------
# 4.3 Analyse geographique
# ------------------------------------------------------------------
ville = df.groupby("ville").agg(
    ca=("chiffre_affaires", lambda s: s[df.loc[s.index, "statut_commande"] != "Annulée"].sum()),
    profit_net=("profit_net", "sum"),
    taux_annulation=("indicateur_annulation", "mean"),
    nb_commandes=("id_commande", "count"),
).reset_index()
ville["taux_annulation"] = (ville["taux_annulation"] * 100).round(2)
ville = ville.sort_values("ca", ascending=False)

ca_mensuel_ville = (
    df[df["statut_commande"] != "Annulée"]
    .groupby(["mois", "ville"])["chiffre_affaires"].sum()
    .reset_index()
)
# croissance juillet -> decembre par ville
piv = ca_mensuel_ville.pivot(index="ville", columns="mois", values="chiffre_affaires").fillna(0)
premier_mois, dernier_mois = sorted(df["mois"].unique())[0], sorted(df["mois"].unique())[-1]
croissance = ((piv[dernier_mois] - piv[premier_mois]) / piv[premier_mois].replace(0, np.nan) * 100).round(2)
ville["croissance_juillet_decembre_pct"] = ville["ville"].map(croissance)

kpis["geographique"] = {
    "table": ville.round(2).to_dict(orient="records"),
    "ville_top_ca": ville.iloc[0]["ville"],
    "ville_meilleure_croissance": ville.sort_values("croissance_juillet_decembre_pct", ascending=False).iloc[0]["ville"],
}

# ------------------------------------------------------------------
# 4.4 Analyse marketing
# ------------------------------------------------------------------
mkt = df.groupby("canal_marketing").agg(
    ca=("chiffre_affaires", lambda s: s[df.loc[s.index, "statut_commande"] != "Annulée"].sum()),
    cout_marketing_total=("cout_marketing", "sum"),
    nb_commandes=("id_commande", "count"),
    nb_clients=("id_client", "nunique"),
).reset_index()
mkt["roi"] = ((mkt["ca"] - mkt["cout_marketing_total"]) / mkt["cout_marketing_total"]).round(3)

# taux de retention par canal = % clients du canal ayant commande plus d'une fois
retention = []
for canal, g in df.groupby("canal_marketing"):
    nb_par_client = g.groupby("id_client")["id_commande"].count()
    retention.append((nb_par_client > 1).mean() * 100)
mkt["taux_retention_pct"] = [round(r, 2) for r in retention]
mkt = mkt.sort_values("roi", ascending=False)

kpis["marketing"] = {
    "table": mkt.round(3).to_dict(orient="records"),
    "canal_meilleur_roi": mkt.iloc[0]["canal_marketing"],
    "canal_pire_roi": mkt.iloc[-1]["canal_marketing"],
}

# ------------------------------------------------------------------
# 4.5 Analyse clients
# ------------------------------------------------------------------
nb_clients_total = df["id_client"].nunique()
nb_par_client = df.groupby("id_client")["id_commande"].count()
pct_recurrents = (nb_par_client > 1).mean() * 100

ca_par_client = (
    df[df["statut_commande"] != "Annulée"]
    .groupby("id_client")["chiffre_affaires"].sum()
    .sort_values(ascending=False)
)
cum_pct_clients = np.arange(1, len(ca_par_client) + 1) / len(ca_par_client) * 100
cum_pct_ca = ca_par_client.cumsum() / ca_par_client.sum() * 100
# % de clients qui generent 80% du CA
idx_80 = np.searchsorted(cum_pct_ca.values, 80)
pct_clients_pour_80pct_ca = round(cum_pct_clients[idx_80], 2) if idx_80 < len(cum_pct_clients) else 100.0

top10 = ca_par_client.head(10).reset_index()
top10.columns = ["id_client", "ca_total"]

# segmentation simple par valeur_vie_client (quantiles)
clv_par_client = df.groupby("id_client")["valeur_vie_client"].first()
segments = pd.qcut(clv_par_client, q=3, labels=["Bronze", "Argent", "Or"])
segment_counts = segments.value_counts().to_dict()

kpis["clients"] = {
    "nb_clients_total": int(nb_clients_total),
    "pct_clients_recurrents": round(pct_recurrents, 2),
    "pct_clients_pour_80pct_ca": pct_clients_pour_80pct_ca,
    "top10_clients": top10.round(2).to_dict(orient="records"),
    "segmentation": {str(k): int(v) for k, v in segment_counts.items()},
}

with open("data/kpis.json", "w", encoding="utf-8") as f:
    json.dump(kpis, f, ensure_ascii=False, indent=2, default=str)

print(json.dumps(kpis["performance_globale"], ensure_ascii=False, indent=2))
print()
print("Categorie prioritaire (CA):", kpis["categorie"]["categorie_prioritaire_ca"])
print("Ville top CA:", kpis["geographique"]["ville_top_ca"])
print("Canal meilleur ROI:", kpis["marketing"]["canal_meilleur_roi"], "/ pire:", kpis["marketing"]["canal_pire_roi"])
print("% clients pour 80% du CA:", kpis["clients"]["pct_clients_pour_80pct_ca"])
