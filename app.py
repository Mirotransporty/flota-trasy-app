import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable

# Maksymalne parametry pojazdów\ nMAX_KG = 1200
MAX_LDM = 4.8

# Lista pojazdów i dni tygodnia
pojazdy = [
    "TK227CK", "TK742AG", "ESI461A", "ESI4217",
    "TK654CH", "TK564CH", "OP4556U", "SB4432V"
]
dni = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]

# Inicjalizacja tabeli zdarzeń (dynamiczna)
if 'events_df' not in st.session_state:
    st.session_state['events_df'] = pd.DataFrame(
        columns=["Vehicle", "Day", "Type", "City", "Masa", "LDM"]
    )

# Edytowalna tabela zdarzeń
events_df = st.data_editor(
    st.session_state['events_df'],
    use_container_width=True,
    key="events",
    num_rows="dynamic"
)

# Walidacja kategorii jeżeli tabela niepusta
if not events_df.empty:
    events_df['Vehicle'] = events_df['Vehicle'].astype(
        pd.CategoricalDtype(categories=pojazdy)
    )
    events_df['Day'] = events_df['Day'].astype(
        pd.CategoricalDtype(categories=dni)
    )
    events_df['Type'] = events_df['Type'].astype(
        pd.CategoricalDtype(categories=["Z", "R"])
    )

st.subheader("🧭 Mapa tras")
mapa = folium.Map(location=[52.0, 19.0], zoom_start=6)

# Geokoder z cache'em\ ngeolocator = Nominatim(user_agent="flota_app")
if 'geo_cache' not in st.session_state:
    st.session_state['geo_cache'] = {}

# Rysowanie tras dla każdego pojazdu
for veh in pojazdy:
    dfv = events_df[events_df['Vehicle'] == veh].dropna(subset=["City", "Day"])
    if dfv.empty:
        continue
    # Sortowanie wg dni\ norder = {day: idx for idx, day in enumerate(dni)}
    dfv = dfv.sort_values('Day', key=lambda col: col.map(order))

    punkty = []
    suma_kg = 0.0
    suma_ldm = 0.0

    for row in dfv.itertuples():
        city = row.City.strip().title()
        coords = st.session_state['geo_cache'].get(city)
        if coords is None:
            try:
                loc = geolocator.geocode(f"{city}, Poland")
                coords = (loc.latitude, loc.longitude) if loc else None
            except GeocoderUnavailable:
                coords = None
            st.session_state['geo_cache'][city] = coords
        if not coords:
            continue

        # Dodanie markera
        popup = (
            f"<b>{veh}</b> {row.Type} {row.Day}<br>"
            f"{city}<br>Masa: {row.Masa} kg | {row.LDM} LDM"
        )
        folium.Marker(
            location=coords,
            popup=popup,
            icon=folium.Icon(color="blue", icon="truck", prefix='fa')
        ).add_to(mapa)

        punkty.append(coords)
        try:
            suma_kg += float(row.Masa)
            suma_ldm += float(row.LDM)
        except:
            pass

    # Rysowanie linii trasy\ nif len(punkty) > 1:
        kolor = "red" if suma_kg > MAX_KG or suma_ldm > MAX_LDM else "green"
        folium.PolyLine(
            punkty,
            color=kolor,
            weight=5,
            opacity=0.8
        ).add_to(mapa)

# Wyświetlenie mapy
st_folium(mapa, width=1000, height=600)

st.caption(
    "Tabela pozwala dodawać wiele zdarzeń (wiele wierszy) dla każdego pojazdu. "
    "Kolumna Type: Z = Załadunek, R = Rozładunek. Masa i LDM to odrębne kolumny. "
    "Geokodowanie dowolnych miast w Polsce."
)
