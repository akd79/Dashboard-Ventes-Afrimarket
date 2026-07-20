# AfriMarket — Résumé exécutif
### Analyse stratégique de 6 mois d'activité commerciale (juillet–décembre 2025)
**Préparé par : Data Analyst — Direction Générale AfriMarket**

---

## 1. Contexte et objectif

AfriMarket est une plateforme e-commerce panafricaine active dans 8 villes d'Afrique
francophone (Abidjan, Brazzaville, Cotonou, Dakar, Douala, Kinshasa, Libreville, Lomé)
et 4 catégories de produits (Électronique, Mode, Beauté, Maison). La direction a demandé
une analyse des 6 derniers mois d'activité pour éclairer ses décisions sur quatre points :
les variations de chiffre d'affaires, le taux de retour, les dépenses marketing et les
écarts de performance entre villes.

Cette analyse s'appuie sur 10 100 commandes brutes, auditées, nettoyées puis enrichies
de 7 indicateurs métier avant d'être exploitées dans 5 axes d'analyse.

## 2. Qualité des données : ce qu'il fallait corriger

Le dataset fourni contenait des défauts représentatifs d'un contexte réel de production :

| Problème | Ampleur | Traitement appliqué |
|---|---|---|
| Doublons stricts | 100 lignes | Suppression |
| Ville mal orthographiée (`Kinshassa`) | 605 lignes | Fusionnée avec `Kinshasa` |
| Catégorie corrompue (`electronique` mélangeant les 4 vraies catégories) | 606 lignes | Reconstruite depuis le nom du produit (fiable à 100 %) |
| Statuts de commande à la casse non uniforme | 100 % des lignes | Casse standardisée |
| Prix unitaire aberrant (valeur sentinelle -50,00 ou signe négatif isolé) | 632 lignes | Imputation par médiane produit / valeur absolue |
| Remise négative (valeur sentinelle -0,10) | 614 lignes | Valeur absolue |
| Quantité nulle (incohérente pour une commande traitée) | 608 lignes | Lignes supprimées |

**700 lignes (6,9 %) ont été retirées du jeu final** (doublons + quantités nulles
incohérentes) ; le dataset propre (`df_clean`, 9 400 lignes) sert de socle à toute
l'analyse qui suit.

> **Hypothèse méthodologique à valider avec la Finance** : le dataset ne fournit pas le
> coût d'achat des produits. La marge brute est donc *estimée* à partir d'un taux de
> marge par catégorie usuel en e-commerce (Électronique 15 %, Mode 45 %, Beauté 55 %,
> Maison 35 %). Tous les chiffres de marge et de profit net de ce document reposent sur
> cette hypothèse et devront être recalés sur les coûts réels dès qu'ils seront disponibles.

## 3. Performance globale

| Indicateur | Valeur |
|---|---|
| Chiffre d'affaires total | **2 496 745 $** |
| Profit net estimé | **363 340 $** (14,6 % du CA) |
| Panier moyen | **270,88 $** |
| Taux d'annulation | **1,95 %** |
| Taux de retour | **8,14 %** |

Le taux d'annulation est faible et ne constitue pas un point d'alerte global. Le taux de
retour (8,14 %) est en revanche significatif et, comme détaillé ci-dessous, concentré sur
une seule catégorie — c'est le vrai signal à traiter.

## 4. Résultats par axe d'analyse

### 4.1 Catégories — un moteur unique, à protéger

`Électronique` pèse **73 % du CA total** (1,82 M$) et reste le premier contributeur
chaque mois sur toute la période. C'est la catégorie prioritaire en termes de budget,
de stock et de visibilité. Mais elle porte aussi le **taux de retour le plus élevé du
catalogue (15,3 %)**, près du double de la moyenne globale et 3 à 5 fois supérieur aux
autres catégories (Beauté 2,8 %, Maison 4,9 %, Mode 7,3 %). Chaque point de retour gagné
sur l'Électronique a un impact financier bien supérieur à un gain équivalent ailleurs :
c'est simultanément la catégorie à **prioriser** (croissance) et à **optimiser en
urgence** (qualité).

### 4.2 Géographie — un marché en croissance freiné par un problème opérationnel local

`Kinshasa` reste le marché n°1 (752 891 $ de CA, quasiment aucune annulation) et doit
être consolidé. Le signal le plus intéressant vient de `Douala` : sa croissance
juillet→décembre est la **plus forte du réseau (+76 %)**, mais son taux d'annulation
(**12,9 %**) est nettement supérieur à toutes les autres villes (0 % ou proche partout
ailleurs). Un problème local (paiement, fiabilité de livraison) freine probablement une
ville qui serait sinon la meilleure dynamique de croissance d'AfriMarket. `Libreville`
recule fortement (-46 %) et mérite un diagnostic avant tout renforcement budgétaire.

### 4.3 Marketing — un budget mal réparti au regard du ROI

| Canal | CA généré | Coût marketing | ROI* | Rétention |
|---|---|---|---|---|
| Email | 527 688 $ | 2 349 $ | **223,6x** | 46,3 % |
| Google Ads | 663 082 $ | 13 159 $ | 49,4x | 50,3 % |
| Instagram Ads | 946 401 $ | 37 637 $ | 24,1x | 54,2 % |
| Influenceur | 359 574 $ | 16 360 $ | 21,0x | 42,4 % |

*ROI = (Revenus − Coût marketing) / Coût marketing. Le coût marketing étant un petit
coût variable par commande (et non un budget de campagne), les valeurs absolues sont
élevées ; c'est le **classement relatif** entre canaux qui est actionnable.

`Instagram Ads` capte **60 % du budget marketing total** pour le ROI le plus faible après
`Influenceur`, avec une rétention équivalente à Email. `Email`, quasiment gratuit, est de
loin le canal le plus rentable et reste sous-exploité. `Influenceur` cumule le pire ROI
et la plus faible rétention client.

### 4.4 Clients — une base fidèle mais concentrée

AfriMarket compte **1 747 clients actifs**, dont **74 % de clients récurrents** — un très
bon signal de satisfaction globale. Le chiffre d'affaires reste toutefois concentré :
**32 % des clients génèrent 80 % du CA** (dynamique proche d'un Pareto 80/20). Le
segment « Or » (tiers supérieur de valeur vie client) constitue le socle de revenus à
sécuriser en priorité ; le segment « Bronze », nombreux mais à faible valeur, représente
le principal gisement de croissance par la fréquence d'achat plutôt que par l'acquisition
de nouveaux clients.

## 5. Recommandations stratégiques

**1. Lancer un plan qualité d'urgence sur la catégorie Électronique**
Auditer les fiches produit, les fournisseurs et le SAV des références au taux de retour
le plus élevé. Objectif : ramener le taux de retour Électronique de 15,3 % vers la
moyenne catalogue (~8 %), ce qui, à volume constant, représenterait un gain de marge
préservée de l'ordre de plusieurs dizaines de milliers de dollars sur 6 mois.

**2. Résoudre le point de friction opérationnel à Douala avant d'investir davantage**
Diagnostiquer la cause des 12,9 % d'annulations (méthode de paiement, délai/fiabilité de
livraison) en priorité sur ce marché. Douala combine la plus forte croissance et le seul
vrai problème de qualité de service : le corriger transformerait potentiellement le
meilleur relais de croissance du réseau.

**3. Réallouer le budget marketing vers les canaux les plus rentables**
Réduire progressivement le budget `Instagram Ads` et `Influenceur` (ROI les plus faibles,
plus de la moitié du budget total) au profit d'`Email` (ROI le plus élevé, quasi gratuit)
et de `Google Ads`. Réaffecter ne serait-ce que 20 % du budget Instagram vers Email
représenterait un gain de ROI significatif à budget marketing global inchangé.

**4. Mettre en place un programme de fidélisation à deux vitesses**
Un programme premium pour le segment « Or » (accès anticipé, livraison prioritaire) pour
sécuriser les 80 % de CA concentrés sur un tiers de la base ; des campagnes de relance et
de cross-sell ciblées pour le segment « Bronze », levier de croissance le moins coûteux
(base client déjà acquise, 74 % de récurrence globale).

**5. Suivre mensuellement 4 indicateurs de pilotage**
Taux de retour Électronique, taux d'annulation Douala, ROI par canal marketing et % de
clients générant 80 % du CA. Ces quatre indicateurs couvrent l'intégralité des
préoccupations initiales de la direction (variations de CA, retours, dépenses marketing,
écarts géographiques) et permettent de mesurer l'impact des actions ci-dessus dans les
prochains cycles.

## 6. Conclusion — passer à l'action

AfriMarket dispose d'une base saine : croissance globale positive, taux d'annulation
faible, forte récurrence client. Les marges de progression identifiées ne sont pas
diffuses mais **concentrées sur quatre leviers précis et immédiatement actionnables** :
la qualité produit en Électronique, la fiabilité opérationnelle à Douala, la réallocation
du budget marketing vers Email/Google Ads, et la fidélisation différenciée par segment de
valeur client. Prioriser ces quatre chantiers dans cet ordre — qualité produit d'abord,
car c'est le poste qui pèse le plus lourd en valeur absolue — permet de transformer cette
analyse en plan d'action trimestriel dès le prochain comité de direction.
