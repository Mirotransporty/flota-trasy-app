
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta

MAX_KG = 1200
MAX_LDM = 4.8

pojazdy = [
    "TK227CK", "TK742AG", "ESI461A", "ESI4217",
    "TK654CH", "TK564CH", "OP4556U", "SB4432V"
]
dni = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]

if "df" not in st.session_state:
    df = pd.DataFrame("" for _ in range(len(pojazdy) * len(dni)))
    df = df.values.reshape(len(pojazdy), len(dni))
    st.session_state.df = pd.DataFrame(df, index=pojazdy, columns=dni)

st.title("🗺️ Plan trasy i obciążenia pojazdów")

st.subheader("📋 Tabela zleceń")
df = st.data_editor(
    st.session_state.df,
    num_rows="fixed",
    use_container_width=True,
    key="editable_table"
)

st.subheader("🧭 Mapa trasy")
mapa = folium.Map(location=[52.0, 19.0], zoom_start=6)

kolory = ["red", "green", "blue", "orange", "purple", "darkred", "cadetblue", "darkgreen"]

for idx, pojazd in enumerate(df.index):
    kolor = kolory[idx % len(kolory)]
    ldm_suma = 0
    kg_suma = 0
    trasa = []
    for dzien in df.columns:
        wpis = df.loc[pojazd, dzien]
        if wpis and any(x in wpis for x in ["->", "-", ","]):
            try:
                czesci = wpis.replace(",", "").split()
                ladunek = [int(s) for s in czesci if s.isdigit()]
                miasta = wpis.split("->")
                miasta = [m.strip() for m in miasta if m.strip()]
                if len(ladunek) >= 2:
                    kg_suma += ladunek[0]
                    ldm_suma += ladunek[1] / 10
                for miasto in miasta:
                    trasa.append(miasto)
            except:
                continue

    popup_text = f"<b>{pojazd}</b><br>Waga: {kg_suma} kg / {MAX_KG}<br>LDM: {ldm_suma:.1f} / {MAX_LDM}"
    color_border = "red" if kg_suma > MAX_KG or ldm_suma > MAX_LDM else kolor

    geolokalizacja = {
        "Jaworzno": [50.205, 19.275],
        "Katowice": [50.2649, 19.0238],
        "Orzesze": [50.1503, 18.7838],
        "Warszawa": [52.2297, 21.0122],
        "Sieradz": [51.5955, 18.7394],
        "Poznań": [52.4064, 16.9252],
        "Łódź": [51.7592, 19.4560],
        "Czeladź": [50.3167, 19.1000],
        "Głuchołazy": [50.3142, 17.3833],
        "Kartuzy": [54.3333, 18.2000],
        "Koźle": [50.3558, 18.2311],
        "Opole": [50.6751, 17.9213],
        "Bielsko-Biała": [49.8225, 19.0444],
        "Puławy": [51.4167, 21.9667]
    }

    wspolrzedne = [geolokalizacja.get(m, [52.0, 19.0]) for m in trasa]
    if wspolrzedne:
        folium.PolyLine(wspolrzedne, color=color_border, weight=5, opacity=0.7).add_to(mapa)
        if wspolrzedne[-1]:
            folium.Marker(
                location=wspolrzedne[-1],
                popup=popup_text,
                icon=folium.Icon(color=color_border)
            ).add_to(mapa)

st_folium(mapa, width=1000, height=600)

st.caption("Legenda: wpisz np. 'Jaworzno -> Katowice 500 15' (gdzie 500 kg i 1.5 LDM)")
