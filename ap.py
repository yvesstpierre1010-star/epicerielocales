import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Campagne Serge Bonin - Optimiseur Terrain", layout="wide")

st.title("📍 Suivi des distributions - Épiceries Chutes-de-la-Chaudière")
st.write("Optimisez la distribution des cartes électorales de Serge Bonin basé sur l'affluence réelle.")

# 1. Données incluses directement dans le code pour éviter toute erreur de fichier externe !
@st.cache_data
def load_data():
    data = {
        'nom': [
            'Maxi Saint-Nicolas', 
            'IGA Extra Famille Rousseau', 
            'Walmart Supercentre Saint-Nicolas', 
            'Metro Plus Charny', 
            'Metro Plus Laroche St-Étienne', 
            'Super C St-Jean-Chrysostome',
            'Épicerie Dumond (Charny)'
        ],
        'adresse': [
            '1235 Avenue De la Concorde, Lévis, QC G7A 4X6',
            '1855 Route des Rivières, Lévis, QC G7A 4X8',
            '1200 Route des Rivières, Lévis, QC G7A 4R8',
            '3333 Chemin de Charny, Lévis, QC G6X 3R7',
            '3045 Route Lagueux, suite 100, Lévis, QC G6J 1K6',
            '820 Avenue Taniata, Lévis, QC G6Z 2E1',
            '2390 Chemin de Charny, Lévis, QC G6X 2R1'
        ],
        'secteur': [
            'Saint-Nicolas', 'Saint-Nicolas', 'Saint-Nicolas', 
            'Charny', 'Saint-Étienne-de-Lauzon', 'Saint-Jean-Chrysostome', 'Charny'
        ],
        'latitude': [46.7022, 46.6942, 46.7001, 46.7150, 46.6578, 46.7331, 46.7051],
        'longitude': [-71.3411, -71.3533, -71.3425, -71.2580, -71.4022, -71.1892, -71.2621],
        'meilleur_creneau': [
            'Vendredi 16h00-18h30 / Samedi 11h00-14h00',
            'Vendredi 15h30-18h00 / Samedi 10h30-13h30',
            'Samedi 11h00-15h00 / Dimanche 12h00-15h00',
            'Jeudi 16h00-18h30 / Samedi 10h00-13h00',
            'Vendredi 15h00-18h00 / Samedi 09h30-12h30',
            'Jeudi 16h30-19h00 / Vendredi 15h30-18h30',
            'Vendredi 16h00-18h00'
        ],
        'statut': ['À faire', 'À faire', 'À faire', 'À faire', 'À faire', 'À faire', 'À faire']
    }
    return pd.DataFrame(data)

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
    st.session_state.df.loc[st.session_state.df['nom'] == epicerie_selectionnee, 'statut'] = 'Visité'
    st.sidebar.success(f"Enregistré ! {nb_cartes} cartes distribuées à {epicerie_selectionnee} par {nom_benevole}.")
    st.rerun()

# 3. Affichage visuel des recommandations (Fenêtres d'affluence)
st.subheader("💡 Fenêtres d'affluence optimales")
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

st_folium(m, width="100%", height=500)
