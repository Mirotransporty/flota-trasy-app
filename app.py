import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Maksymalne parametry
MAX_KG = 1200
MAX_LDM = 4.8

# Lista pojazdów i dni tygodnia
pojazdy = [
    "TK227CK", "TK742AG", "ESI461A", "ESI4217",
    "TK654CH", "TK564CH", "OP4556U", "SB4432V"
]
dni = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]

# Przygotowanie DataFrame z płaskimi nazwami kolumn dni_Miasto, dni_Masa, dni_LDM
data = {}
for dzien in dni:
    data[f"{dzien}_Miasto"] = ["" for _ in pojazdy]
    data[f"{dzien}_Masa"] = ["" for _ in pojazdy]
    data[f"{dzien}_LDM"] = ["" for _ in pojazdy]

df = pd.DataFrame(data, index=pojazdy)

st.title("🗺️ Plan trasy i obciążenia pojazdów")
st.subheader("📋 Tabela zleceń")
# Edytowalna tabela
edited_df = st.data_editor(
    df,
    num_rows="fixed",
    use_container_width=True,
    key="tabela_zlecen"
)

st.subheader("🧭 Mapa trasy")
mapa = folium.Map(location=[52.0, 19.0], zoom_start=6)

# Przygotowanie kolorów i przykładowej geolokalizacji
kolory = ["red", "green", "blue", "orange", "purple", "darkred", "cadetblue", "darkgreen"]
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

# Rysowanie tras
for idx, pojazd in enumerate(pojazdy):
    kolor = kolory[idx % len(kolory)]
    suma_kg = 0.0
    suma_ldm = 0.0
    punkty = []

    for dzien in dni:
        miasto = str(edited_df.at[pojazd, f"{dzien}_Miasto"]).strip().title()
        masa = edited_df.at[pojazd, f"{dzien}_Masa"]
        ldm = edited_df.at[pojazd, f"{dzien}_LDM"]

        # Dodaj punkt, jeśli miasto jest w geolokalizacji
        if miasto and miasto in geolokalizacja:
            wsp = geolokalizacja[miasto]
            popup = (f"<b>{pojazd}</b><br>" +
                     f"{dzien}: {miasto}<br>" +
                     f"Masa: {masa} kg<br>LDM: {ldm}")
            folium.Marker(
                location=wsp,
                popup=popup,
                icon=folium.Icon(color=kolor)
            ).add_to(mapa)
            punkty.append(wsp)
            # Sumuj wartości, jeśli są liczbami
            try:
                suma_kg += float(masa)
                suma_ldm += float(ldm)
            except:
                pass

    # Rysuj linię, jeśli co najmniej 2 punkty
    if len(punkty) > 1:
        color_border = "red" if suma_kg > MAX_KG or suma_ldm > MAX_LDM else kolor
        folium.PolyLine(
            punkty,
            color=color_border,
            weight=5,
            opacity=0.8
        ).add_to(mapa)

# Wyświetl mapę
st_folium(mapa, width=1000, height=600)

st.caption(
    "Wprowadź dla każdego dnia: Miasto oraz wartości Masa (kg) i LDM. "
    "Trasa będzie rysowana automatycznie, a przeciążenia oznaczone czerwoną linią."
)
