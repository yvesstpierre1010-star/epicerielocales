import streamlit as True
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Campagne Serge Bonin - Optimiseur Terrain", layout="wide")

st.title("📍 Suivi des distributions - Épiceries Chutes-de-la-Chaudière")
st.write("Optimisez la distribution des cartes électorales de Serge Bonin basé sur l'affluence réelle.")

# 1. Chargement dynamique du fichier CSV généré
@st.cache_data
def load_data():
    # Lit directement le fichier CSV que je vous ai préparé
    return pd.read_csv("epiceries_chutes_chaudiere.csv")

# Initialisation des données dans la session Streamlit pour permettre la modification dynamique
if 'df' not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# 2. Barre latérale (Sidebar) pour enregistrer une action terrain
st.sidebar.header("📝 Marquer une distribution")
epicerie_selectionnee = st.sidebar.selectbox("Choisir l'épicerie", df['nom'].tolist())
date_visite = st.sidebar.date_input("Date de la distribution")
nb_cartes = st.sidebar.number_input("Nombre de cartes distribuées", min_value=0, step=10, value=50)
nom_benevole = st.sidebar.text_input("Nom du bénévole / Équipe")

if st.sidebar.button("Enregistrer la visite"):
    # Met à jour le statut dans l'application en mémoire
    st.session_state.df.loc[st.session_state.df['nom'] == epicerie_selectionnee, 'statut'] = 'Visité'
    st.sidebar.success(f"Enregistré ! {nb_cartes} cartes distribuées à {epicerie_selectionnee} par {nom_benevole}.")
    st.rerun()

# 3. Affichage visuel des recommandations (Fenêtres d'affluence)
st.subheader("💡 Fenêtres d'affluence optimales")
# On crée une grille de colonnes dynamiques
cols = st.columns(len(df))
for idx, row in df.iterrows():
    with cols[idx]:
        couleur = "🔴" if row['statut'] == "À faire" else "🟢"
        st.metric(
            label=f"{couleur} {row['nom']}", 
            value=row['secteur'], 
            delta=f"Top: {row['meilleur_creneau']}",
            delta_color="off"
        )

# 4. Cartographie interactive 100 % gratuite (Folium / Leaflet)
st.subheader("🗺️ Carte de suivi de la circonscription")
# Centré sur le cœur géographique de Chutes-de-la-Chaudière (Lévis)
m = folium.Map(location=[46.6980, -71.3200], zoom_start=12)

for idx, row in df.iterrows():
    icon_color = 'red' if row['statut'] == 'À faire' else 'green'
    popup_text = f"""
    <div style='font-family: sans-serif; min-width: 200px;'>
        <b>{row['nom']}</b><br>
        <i>{row['adresse']}</i><br><br>
        <b>Meilleur moment :</b> {row['meilleur_creneau']}<br>
        <b>Statut actuel :</b> {row['statut']}
    </div>
    """
    
    folium.Marker(
        [row['latitude'], row['longitude']],
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=row['nom'],
        icon=folium.Icon(color=icon_color, icon='shopping-cart', prefix='fa')
    ).add_to(m)

# Rendu cartographique
st_folium(m, width="100%", height=500)