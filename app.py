import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from st_aggrid import AgGrid

# ---------- Parametry ----------
MAX_KG   = 1200
MAX_LDM  = 4.8
vehicles = ["TK227CK","TK742AG","ESI461A","ESI4217","TK654CH","TK564CH","OP4556U","SB4432V"]
days     = ["Poniedziałek","Wtorek","Środa","Czwartek","Piątek","Sobota","Niedziela"]
cities   = ["Warszawa","Kraków","Łódź","Wrocław","Poznań","Gdańsk",
            "Szczecin","Bydgoszcz","Lublin","Białystok","Katowice"]

# Inicjuj pusty DF zdarzeń
if "events" not in st.session_state:
    st.session_state.events = pd.DataFrame(
        columns=["Vehicle","Day","Miejsce","Type","Masa","LDM"]
    )

df = st.session_state.events

# Konfiguracja AG-Grid
from st_aggrid.grid_options_builder import GridOptionsBuilder

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("Vehicle",
    rowGroup=True, hide=True
)
gb.configure_column("Day",
    cellEditor="agSelectCellEditor",
    cellEditorParams={"values": days}
)
gb.configure_column("Miejsce",
    cellEditor="agRichSelectCellEditor",
    cellEditorParams={"values": cities}
)
gb.configure_column("Type",
    cellEditor="agSelectCellEditor",
    cellEditorParams={"values": ["Z","R"]}
)
gb.configure_column("Masa", type=["numericColumn","numberColumnFilter"])
gb.configure_column("LDM",  type=["numericColumn","numberColumnFilter"])
gb.configure_grid_options(groupDisplayType="singleColumn")

gridOptions = gb.build()

st.title("🎯 Harmonogram zdarzeń (grupy po pojazdach)")
res = AgGrid(
    df,
    gridOptions=gridOptions,
    update_mode="MODEL_CHANGED",
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,
    theme="material"
)

# Zapisz zaktualizowany DF
st.session_state.events = pd.DataFrame(res["data"])

# ---------- Rysowanie mapy ----------
st.subheader("🗺️ Mapa tras")
m = folium.Map(location=[52,19], zoom_start=6)
geolocator = Nominatim(user_agent="flota_app")
cache = {}

for row in st.session_state.events.itertuples():
    city = row.Miejsce.strip().title()
    if not city: continue

    # geokoduj
    coords = cache.get(city)
    if coords is None:
        loc = geolocator.geocode(f"{city}, Poland")
        coords = (loc.latitude, loc.longitude) if loc else None
        cache[city] = coords
    if not coords: continue

    popup = (f"<b>{row.Vehicle}</b> {row.Type} {row.Day}<br>"
             f"{city}<br>Masa: {row.Masa} kg<br>LDM: {row.LDM}")
    folium.Marker(coords, popup=popup, icon=folium.Icon(color="blue",icon="truck",prefix="fa")).add_to(m)

# linię rysujemy tylko jeśli 2+ punkty tego samego pojazdu
for veh in vehicles:
    pts = [cache[row.Miejsce.strip().title()] 
           for row in st.session_state.events.itertuples() 
           if row.Vehicle==veh and cache.get(row.Miejsce.strip().title())]
    # sumy
    band = st.session_state.events[st.session_state.events.Vehicle==veh]
    total_kg = band.Masa.sum()
    total_ldm = band.LDM.sum()
    if len(pts)>1:
        color = "red" if total_kg>MAX_KG or total_ldm>MAX_LDM else "green"
        folium.PolyLine(pts, color=color, weight=4, opacity=0.7).add_to(m)

st_folium(m, width=1000, height=600)
