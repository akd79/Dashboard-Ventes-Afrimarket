"""
Feature engineering - AfriMarket
Lit data/df_clean.csv, ajoute les features metier, ecrit data/df_features.csv
"""
import pandas as pd
import numpy as np

df = pd.read_csv("data/df_clean.csv", parse_dates=["date_commande"])

# ------------------------------------------------------------------
# Hypothese metier : le dataset ne fournit pas le cout d'achat produit
# (COGS). La marge brute est donc ESTIMEE via un taux de marge par
# categorie, hypothese standard e-commerce a valider avec la Finance :
#   Electronique : 15% (tickets eleves, marge faible, concurrence forte)
#   Mode         : 45%
#   Beaute       : 55% (marge la plus elevee, cout matiere faible)
#   Maison       : 35%
# ------------------------------------------------------------------
TAUX_MARGE = {
    "Électronique": 0.15,
    "Mode": 0.45,
    "Beauté": 0.55,
    "Maison": 0.35,
}

# 1. chiffre_affaires (ligne) = prix * qte * (1 - remise)
df["chiffre_affaires"] = df["prix_unitaire"] * df["quantite"] * (1 - df["remise"])

# 2. marge_brute estimee
df["taux_marge"] = df["categorie"].map(TAUX_MARGE)
df["marge_brute"] = df["chiffre_affaires"] * df["taux_marge"]

# 3. profit_net estime
#    - Livree   : marge - cout_livraison - cout_marketing
#    - Retournee: la marge est perdue (produit renvoye), les couts sont
#                 deja engages et non recuperables -> -livraison -marketing
#    - Annulee  : jamais expediee -> pas de cout de livraison, seul le
#                 cout marketing (deja depense) est perdu
df["profit_net"] = np.select(
    [
        df["statut_commande"] == "Annulée",
        df["statut_commande"] == "Retournée",
    ],
    [
        -df["cout_marketing"],
        -df["cout_livraison"] - df["cout_marketing"],
    ],
    default=df["marge_brute"] - df["cout_livraison"] - df["cout_marketing"],
)

# 4. mois
df["mois"] = df["date_commande"].dt.to_period("M").astype(str)

# 5. indicateur_retour
df["indicateur_retour"] = (df["statut_commande"] == "Retournée").astype(int)
df["indicateur_annulation"] = (df["statut_commande"] == "Annulée").astype(int)

# 6. nombre_commandes_par_client (toutes commandes, y compris annulees/retournees)
cmd_par_client = df.groupby("id_client")["id_commande"].transform("count")
df["nombre_commandes_par_client"] = cmd_par_client

# 7. valeur_vie_client (CLV simplifiee) = somme du CA reellement realise
#    (Livree + Retournee, la vente a eu lieu) par client, sur les 6 mois
ca_realise_ligne = df["chiffre_affaires"].where(df["statut_commande"] != "Annulée", 0)
df["_ca_realise_ligne"] = ca_realise_ligne
clv = df.groupby("id_client")["_ca_realise_ligne"].transform("sum")
df["valeur_vie_client"] = clv
df = df.drop(columns=["_ca_realise_ligne"])

df.to_csv("data/df_features.csv", index=False)

print("OK - df_features genere :", df.shape)
print(df[[
    "chiffre_affaires", "marge_brute", "profit_net", "mois",
    "indicateur_retour", "nombre_commandes_par_client", "valeur_vie_client",
]].head(3).to_string())
