"""
Dashboard interactif Streamlit - AfriMarket
Lancement : streamlit run dashboard/app.py
"""
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "df_features.csv"

st.set_page_config(page_title="AfriMarket - Dashboard Analytique", layout="wide", page_icon="📊")


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["date_commande"])
    return df


df = load_data()

# ------------------------------------------------------------------
# Sidebar - filtres
# ------------------------------------------------------------------
st.sidebar.title("Filtres")

date_min, date_max = df["date_commande"].min(), df["date_commande"].max()
date_range = st.sidebar.date_input(
    "Période", value=(date_min, date_max), min_value=date_min, max_value=date_max
)

villes = st.sidebar.multiselect("Ville", sorted(df["ville"].unique()), default=list(sorted(df["ville"].unique())))
categories = st.sidebar.multiselect("Catégorie", sorted(df["categorie"].unique()), default=list(sorted(df["categorie"].unique())))
canaux = st.sidebar.multiselect("Canal marketing", sorted(df["canal_marketing"].unique()), default=list(sorted(df["canal_marketing"].unique())))

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start, end = date_min, date_max

mask = (
    df["date_commande"].between(start, end)
    & df["ville"].isin(villes)
    & df["categorie"].isin(categories)
    & df["canal_marketing"].isin(canaux)
)
dff = df.loc[mask]

if dff.empty:
    st.warning("Aucune donnée pour cette combinaison de filtres.")
    st.stop()

valides = dff[dff["statut_commande"] != "Annulée"]

# ------------------------------------------------------------------
# Header + KPI
# ------------------------------------------------------------------
st.title("📊 AfriMarket — Dashboard Analytique")
st.caption("Analyse stratégique du e-commerce panafricain — données nettoyées (df_clean)")

ca_total = valides["chiffre_affaires"].sum()
profit_net_total = dff["profit_net"].sum()
panier_moyen = valides["chiffre_affaires"].sum() / max(len(valides), 1)
taux_annulation = (dff["statut_commande"] == "Annulée").mean() * 100
taux_retour = (dff["statut_commande"] == "Retournée").mean() * 100

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("CA total", f"{ca_total:,.0f} $")
c2.metric("Profit net estimé", f"{profit_net_total:,.0f} $")
c3.metric("Panier moyen", f"{panier_moyen:,.2f} $")
c4.metric("Taux d'annulation", f"{taux_annulation:.1f} %")
c5.metric("Taux de retour", f"{taux_retour:.1f} %")

st.divider()

tab_cat, tab_geo, tab_mkt, tab_clients = st.tabs(
    ["🏷️ Catégories", "🌍 Géographie", "📣 Marketing", "👥 Clients"]
)

# ------------------------------------------------------------------
# Onglet Catégories
# ------------------------------------------------------------------
with tab_cat:
    cat_stats = valides.groupby("categorie").agg(
        ca=("chiffre_affaires", "sum"),
        nb_commandes=("id_commande", "count"),
    ).reset_index()
    taux_retour_cat = dff.groupby("categorie")["indicateur_retour"].mean().mul(100).reset_index()
    cat_stats = cat_stats.merge(taux_retour_cat, on="categorie")
    cat_stats = cat_stats.sort_values("ca", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(cat_stats, x="categorie", y="ca", title="CA par catégorie", color="categorie")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(cat_stats, x="categorie", y="indicateur_retour", title="Taux de retour par catégorie (%)", color="categorie")
        st.plotly_chart(fig, use_container_width=True)

    evo = valides.groupby(["mois", "categorie"])["chiffre_affaires"].sum().reset_index()
    fig = px.line(evo, x="mois", y="chiffre_affaires", color="categorie", markers=True, title="Évolution mensuelle du CA par catégorie")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(cat_stats.rename(columns={"ca": "CA ($)", "nb_commandes": "Nb commandes", "indicateur_retour": "Taux retour (%)"}), use_container_width=True)

# ------------------------------------------------------------------
# Onglet Géographie
# ------------------------------------------------------------------
with tab_geo:
    ville_stats = valides.groupby("ville").agg(ca=("chiffre_affaires", "sum"), profit_net=("profit_net", "sum")).reset_index()
    annulation_ville = dff.groupby("ville")["indicateur_annulation"].mean().mul(100).reset_index()
    ville_stats = ville_stats.merge(annulation_ville, on="ville").sort_values("ca", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(ville_stats, x="ville", y="ca", title="CA par ville", color="ville")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(ville_stats, x="ville", y="indicateur_annulation", title="Taux d'annulation par ville (%)", color="ville")
        st.plotly_chart(fig, use_container_width=True)

    evo_ville = valides.groupby(["mois", "ville"])["chiffre_affaires"].sum().reset_index()
    fig = px.line(evo_ville, x="mois", y="chiffre_affaires", color="ville", markers=True, title="Évolution mensuelle du CA par ville")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(ville_stats.rename(columns={"ca": "CA ($)", "profit_net": "Profit net ($)", "indicateur_annulation": "Taux annulation (%)"}), use_container_width=True)

# ------------------------------------------------------------------
# Onglet Marketing
# ------------------------------------------------------------------
with tab_mkt:
    mkt_stats = valides.groupby("canal_marketing").agg(ca=("chiffre_affaires", "sum")).reset_index()
    cout_mkt = dff.groupby("canal_marketing")["cout_marketing"].sum().reset_index()
    mkt_stats = mkt_stats.merge(cout_mkt, on="canal_marketing")
    mkt_stats["roi"] = (mkt_stats["ca"] - mkt_stats["cout_marketing"]) / mkt_stats["cout_marketing"]
    mkt_stats = mkt_stats.sort_values("roi", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(mkt_stats, x="canal_marketing", y="roi", title="ROI par canal marketing", color="canal_marketing")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.pie(mkt_stats, names="canal_marketing", values="cout_marketing", title="Répartition du coût marketing par canal")
        st.plotly_chart(fig, use_container_width=True)

    st.caption("ROI = (Revenus - Coût marketing) / Coût marketing. Le coût marketing étant un petit coût variable par commande, "
               "les valeurs de ROI sont élevées en absolu : c'est le classement relatif entre canaux qui est actionnable.")
    st.dataframe(mkt_stats.rename(columns={"ca": "CA ($)", "cout_marketing": "Coût marketing ($)", "roi": "ROI (x)"}), use_container_width=True)

# ------------------------------------------------------------------
# Onglet Clients
# ------------------------------------------------------------------
with tab_clients:
    nb_clients = dff["id_client"].nunique()
    nb_par_client = dff.groupby("id_client")["id_commande"].count()
    pct_recurrents = (nb_par_client > 1).mean() * 100

    ca_par_client = valides.groupby("id_client")["chiffre_affaires"].sum().sort_values(ascending=False)
    cum_pct_clients = np.arange(1, len(ca_par_client) + 1) / len(ca_par_client) * 100
    cum_pct_ca = ca_par_client.cumsum() / ca_par_client.sum() * 100

    k1, k2 = st.columns(2)
    k1.metric("Nombre de clients", f"{nb_clients:,}")
    k2.metric("% de clients récurrents", f"{pct_recurrents:.1f} %")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(x=cum_pct_clients, y=cum_pct_ca, title="Courbe de Pareto — concentration du CA par client",
                      labels={"x": "% de clients", "y": "% cumulé du CA"})
        fig.add_hline(y=80, line_dash="dash", line_color="red")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        top10 = ca_par_client.head(10).reset_index()
        top10.columns = ["id_client", "ca_total"]
        fig = px.bar(top10, x="id_client", y="ca_total", title="Top 10 clients par CA")
        st.plotly_chart(fig, use_container_width=True)

    clv_par_client = dff.groupby("id_client")["valeur_vie_client"].first()
    if clv_par_client.nunique() >= 3:
        segments = pd.qcut(clv_par_client, q=3, labels=["Bronze", "Argent", "Or"])
        seg_counts = segments.value_counts().reindex(["Bronze", "Argent", "Or"]).reset_index()
        seg_counts.columns = ["segment", "nb_clients"]
        fig = px.bar(seg_counts, x="segment", y="nb_clients", title="Segmentation clients (CLV)", color="segment")
        st.plotly_chart(fig, use_container_width=True)
