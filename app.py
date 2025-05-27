import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from st_aggrid import AgGrid, GridOptionsBuilder

# ---------- Parametry ----------
MAX_KG = 1200
MAX_LDM = 4.8

vehicles = ["TK227CK","TK742AG","ESI461A","ESI4217","TK654CH","TK564CH","OP4556U","SB4432V"]
days     = ["Poniedziałek","Wtorek","Środa","Czwartek","Piątek","Sobota","Niedziela"]
slots    = list(range(1,6))
polish_cities = [
    "Warszawa","Kraków","Łódź","Wrocław","Poznań","Gdańsk",
    "Szczecin","Bydgoszcz","Lublin","Białystok","Katowice",
    "Bielsko-Biała","Rzeszów","Olsztyn","Opole","Kielce","Zielona Góra"
]

# ---------- Budowa DataFrame ----------

# Kolumny: Vehicle + dla każdego dnia i slotu cztery pola
cols = ["Vehicle"]
for d in days:
    for s in slots:
        cols += [f"{d}_{s}_City", f"{d}_{s}_Type", f"{d}_{s}_Masa", f"{d}_{s}_LDM"]

# Inicjalizacja pustych danych
if "df" not in st.session_state:
    data = []
    for v in vehicles:
        row = {"Vehicle": v}
        for c in cols[1:]:
            # domyślnie puste pola; numeric columns możemy zostawić jako NaN
            row[c] = "" 
        data.append(row)
    st.session_state.df = pd.DataFrame(data, columns=cols)

df = st.session_state.df

# ---------- AgGrid konfiguracja ----------
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("Vehicle", header_name="Pojazd", editable=False)
# Pozostałe kolumny edytowalne
for d in days:
    for s in slots:
        city_col = f"{d}_{s}_City"
        type_col = f"{d}_{s}_Type"
        masa_col = f"{d}_{s}_Masa"
        ldm_col = f"{d}_{s}_LDM"

        gb.configure_column(city_col,
            header_name=f"{d} #{s} Miejsce",
            editable=True,
            cellEditor="agRichSelectCellEditor",
            cellEditorParams={"values": polish_cities}
        )
        gb.configure_column(type_col,
            header_name=f"{d} #{s} Z/R",
            editable=True,
            cellEditor="agSelectCellEditor",
            cellEditorParams={"values": ["Z","R"]}
        )
        gb.configure_column(masa_col,
            header_name=f"{d} #{s} Masa",
            editable=True,
            type=["numericColumn","numberColumnFilter","rightAligned"]
        )
        gb.configure_column(ldm_col,
            header_name=f"{d} #{s} LDM",
            editable=True,
            type=["numericColumn","numberColumnFilter","rightAligned"]
        )

gridOptions = gb.build()

st.title("🗺️ Plan trasy i obciążenia pojazdów")
st.subheader("📋 Siatka z 5 slotami dziennie (max 5 zdarzeń)")

# Rysowanie tabeli
grid_response = AgGrid(
    df,
    gridOptions=gridOptions,
    enable_enterprise_modules=False,
    update_mode="MODEL_CHANGED",
    allow_unsafe_jscode=True,
    theme="material"
)
df = grid_response["data"]
st.session_state.df = df.copy()

# ---------- Generowanie mapy trasy ----------
st.subheader("🧭 Mapa tras")
m = folium.Map(location=[52.0,19.0], zoom_start=6)
geolocator = Nominatim(user_agent="flota_app")
if "geo_cache" not in st.session_state:
    st.session_state.geo_cache = {}

for v in vehicles:
    # Zbierz punkty w kolejności dni, slotów
    points = []
    suma_kg = 0.0
    suma_ldm = 0.0

    for d in days:
        for s in slots:
            city = str(df.loc[df["Vehicle"]==v, f"{d}_{s}_City"].values[0]).strip().title()
            typ  = str(df.loc[df["Vehicle"]==v, f"{d}_{s}_Type"].values[0]).upper()
            try:
                masa = float(df.loc[df["Vehicle"]==v, f"{d}_{s}_Masa"].values[0])
            except:
                masa = 0.0
            try:
                ldm  = float(df.loc[df["Vehicle"]==v, f"{d}_{s}_LDM"].values[0])
            except:
                ldm  = 0.0

            if city:
                # Geokodowanie
                coords = st.session_state.geo_cache.get(city)
                if coords is None:
                    try:
                        loc = geolocator.geocode(f"{city}, Poland")
                        coords = (loc.latitude, loc.longitude) if loc else None
                    except:
                        coords = None
                    st.session_state.geo_cache[city] = coords
                if not coords:
                    continue

                # Dodaj marker
                popup = f"<b>{v}</b> {typ} {d} (slot {s})<br>{city}<br>Masa: {masa}kg<br>LDM: {ldm}"
                folium.Marker(
                    location=coords,
                    popup=popup,
                    icon=folium.Icon(color="blue", icon="truck", prefix="fa")
                ).add_to(m)

                points.append(coords)
                suma_kg  += masa
                suma_ldm += ldm

    # Rysuj linię, jeśli są co najmniej 2 punkty
    if len(points) > 1:
        color = "red" if suma_kg>MAX_KG or suma_ldm>MAX_LDM else "green"
        folium.PolyLine(points, color=color, weight=4, opacity=0.7).add_to(m)

st_folium(m, width=1000, height=600)
st.caption(
    "Autocomplete Miasta – wpisz kilka liter, wybierz z listy.\n"
    "Z/R = Z (Załadunek) / R (Rozładunek). Rama 5 slotów dziennie."
)
