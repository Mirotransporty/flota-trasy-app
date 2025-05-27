# app.py

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from st_aggrid import AgGrid

# -------------- PARAMETRY --------------
MAX_KG   = 1200
MAX_LDM  = 4.8

vehicles = ["TK227CK","TK742AG","ESI461A","ESI4217","TK654CH","TK564CH","OP4556U","SB4432V"]
days     = ["Poniedziałek","Wtorek","Środa","Czwartek","Piątek","Sobota","Niedziela"]
slots    = list(range(1,6))

# Przykładowa lista miast (można rozbudować)
cities = [
    "Warszawa","Kraków","Łódź","Wrocław","Poznań","Gdańsk",
    "Szczecin","Bydgoszcz","Lublin","Białystok","Katowice",
    "Bielsko-Biała","Rzeszów","Olsztyn","Opole","Kielce","Zielona Góra"
]

# -------------- INICJALIZACJA DATAFRAME --------------
cols = ["Vehicle"]
for d in days:
    for s in slots:
        prefix = f"{d}#{s}"
        cols += [f"{prefix}_City", f"{prefix}_Type", f"{prefix}_Masa", f"{prefix}_LDM"]

if "df" not in st.session_state:
    df0 = pd.DataFrame([{c: "" for c in cols} for _ in vehicles], columns=cols)
    df0["Vehicle"] = vehicles
    st.session_state.df = df0

df = st.session_state.df

# -------------- KONFIGURACJA AG-GRID --------------
columnDefs = [
    {
        "headerName": "Pojazd",
        "field": "Vehicle",
        "pinned": "left",
        "editable": False,
        "lockPosition": True,
        "cellStyle": {"fontWeight": "bold"}
    }
]
for d in days:
    children = []
    for s in slots:
        prefix = f"{d}#{s}"
        children += [
            {
                "headerName": f"#{s} Miejsce",
                "field": f"{prefix}_City",
                "cellEditor": "agRichSelectCellEditor",
                "cellEditorParams": {"values": cities},
                "editable": True
            },
            {
                "headerName": f"#{s} Z/R",
                "field": f"{prefix}_Type",
                "cellEditor": "agSelectCellEditor",
                "cellEditorParams": {"values": ["Z", "R"]},
                "editable": True
            },
            {
                "headerName": f"#{s} Masa",
                "field": f"{prefix}_Masa",
                "type": ["numericColumn", "numberColumnFilter"],
                "editable": True
            },
            {
                "headerName": f"#{s} LDM",
                "field": f"{prefix}_LDM",
                "type": ["numericColumn", "numberColumnFilter"],
                "editable": True
            },
        ]
    columnDefs.append({"headerName": d, "children": children})

gridOptions = {
    "columnDefs": columnDefs,
    "defaultColDef": {"sortable": True, "filter": True, "resizable": True},
    "suppressRowClickSelection": True,
    "rowSelection": "single",
}

st.title("📋 Siatka z 5 slotami dziennie")
grid_response = AgGrid(
    df,
    gridOptions=gridOptions,
    update_mode="MODEL_CHANGED",
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,
    theme="material"
)
st.session_state.df = pd.DataFrame(grid_response["data"])

# -------------- RYSOWANIE MAPY --------------
st.subheader("🧭 Mapa tras")
m = folium.Map(location=[52.0, 19.0], zoom_start=6)
geolocator = Nominatim(user_agent="flota_app")
geo_cache = {}

for _, row in st.session_state.df.iterrows():
    veh = row["Vehicle"]
    punkty = []
    suma_kg = 0.0
    suma_ldm = 0.0

    for d in days:
        for s in slots:
            key_city = f"{d}#{s}_City"
            key_type = f"{d}#{s}_Type"
            key_masa = f"{d}#{s}_Masa"
            key_ldm  = f"{d}#{s}_LDM"

            city = str(row.get(key_city, "")).strip().title()
            typ  = str(row.get(key_type, "")).upper()
            try:
                masa = float(row.get(key_masa, 0))
            except:
                masa = 0.0
            try:
                ldm = float(row.get(key_ldm, 0))
            except:
                ldm = 0.0

            if city:
                coords = geo_cache.get(city)
                if coords is None:
                    loc = geolocator.geocode(f"{city}, Poland")
                    coords = (loc.latitude, loc.longitude) if loc else None
                    geo_cache[city] = coords
                if not coords:
                    continue

                popup = (
                    f"<b>{veh}</b> {typ} {d} (slot {s})<br>"
                    f"{city}<br>Masa: {masa} kg<br>LDM: {ldm}"
                )
                folium.Marker(
                    location=coords,
                    popup=popup,
                    icon=folium.Icon(color="blue", icon="truck", prefix="fa")
                ).add_to(m)
                punkty.append(coords)
                suma_kg += masa
                suma_ldm += ldm

    if len(punkty) > 1:
        kolor = "red" if (suma_kg > MAX_KG or suma_ldm > MAX_LDM) else "green"
        folium.PolyLine(punkty, color=kolor, weight=4, opacity=0.7).add_to(m)

st_folium(m, width=1000, height=600)
st.caption("Legenda: zielona – OK; czerwona – przeciążenie (1.2t / 4.8 LDM).")
