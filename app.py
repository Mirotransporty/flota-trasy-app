import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from st_aggrid import AgGrid

# maksymalne parametry
MAX_KG = 1200
MAX_LDM = 4.8

# konfiguracja
vehicles = ["TK227CK","TK742AG","ESI461A","ESI4217","TK654CH","TK564CH","OP4556U","SB4432V"]
days     = ["Poniedziałek","Wtorek","Środa","Czwartek","Piątek","Sobota","Niedziela"]
slots    = list(range(1,6))
cities   = ["Warszawa","Kraków","Łódź","Wrocław","Poznań","Gdańsk","Szczecin","Bydgoszcz","Lublin","Białystok","Katowice"]

# inicjalizacja pustego DF
cols = ["Vehicle"]
for d in days:
    for s in slots:
        cols += [f"{d}#{s}_City", f"{d}#{s}_Type", f"{d}#{s}_Masa", f"{d}#{s}_LDM"]
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame([{c: "" for c in cols} for _ in vehicles], index=vehicles).assign(Vehicle=vehicles)

df = st.session_state.df

# budowa columnDefs z grupowaniem
columnDefs = [
    {"headerName":"Pojazd","field":"Vehicle","rowDrag":False,"lockPosition":"left","pinned":"left","editable":False}
]
for d in days:
    children = []
    for s in slots:
        children += [
            {
              "headerName":f"#{s} Miejsce",
              "field":f"{d}#{s}_City",
              "cellEditor":"agRichSelectCellEditor",
              "cellEditorParams":{"values":cities},
              "editable":True
            },
            {
              "headerName":f"#{s} Z/R",
              "field":f"{d}#{s}_Type",
              "cellEditor":"agSelectCellEditor",
              "cellEditorParams":{"values":["Z","R"]},
              "editable":True
            },
            {
              "headerName":f"#{s} Masa",
              "field":f"{d}#{s}_Masa",
              "type":["numericColumn","numberColumnFilter"],
              "editable":True
            },
            {
              "headerName":f"#{s} LDM",
              "field":f"{d}#{s}_LDM",
              "type":["numericColumn","numberColumnFilter"],
              "editable":True
            },
        ]
    columnDefs.append({"headerName": d, "children": children})

gridOptions = {
    "columnDefs": columnDefs,
    "defaultColDef": {"sortable":True, "filter":True, "resizable":True},
    "suppressRowClickSelection": True,
    "rowSelection": "multiple",
}

st.title("📋 Siatka z 5 slotami dziennie")
grid_response = AgGrid(
    df.reset_index(drop=True),
    gridOptions=gridOptions,
    update_mode="MODEL_CHANGED",
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,
    theme="material"
)
df = grid_response["data"]
st.session_state.df = df.set_index("Vehicle")

# teraz budujemy mapę analogicznie do poprzedniego przykładu...
# (geokodowanie, pętla po pojazdach, rysowanie markerów i PolyLine)
