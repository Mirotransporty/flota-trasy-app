# … (wcześniej masz definicję df, columnDefs itd.)

grid_response = AgGrid(
    df,
    gridOptions=gridOptions,
    update_mode="MODEL_CHANGED",
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,     # to rozciąga kolumny
    theme="material"
)
st.session_state.df = pd.DataFrame(grid_response["data"])

# ---------- MAPA tras ----------
st.subheader("🧭 Mapa tras")
m = folium.Map(location=[52.0,19.0], zoom_start=6)
geolocator = Nominatim(user_agent="flota_app")
geo_cache = {}

for idx, row in st.session_state.df.iterrows():
    veh = row["Vehicle"]
    punkty = []
    suma_kg = 0.0
    suma_ldm = 0.0

    # dla każdego dnia i slotu buduj klucze
    for d in days:
        for s in slots:
            key_city = f"{d}#{s}_City"
            key_type = f"{d}#{s}_Type"
            key_masa = f"{d}#{s}_Masa"
            key_ldm  = f"{d}#{s}_LDM"

            city = str(row.get(key_city,"")).strip().title()
            typ  = str(row.get(key_type,"")).upper()
            try: masa = float(row.get(key_masa,0))
            except: masa = 0.0
            try: ldm  = float(row.get(key_ldm,0))
            except: ldm  = 0.0

            if city:
                # geokodowanie z cache
                coords = geo_cache.get(city)
                if coords is None:
                    loc = geolocator.geocode(f"{city}, Poland")
                    coords = (loc.latitude, loc.longitude) if loc else None
                    geo_cache[city] = coords
                if not coords:
                    continue

                # marker na mapie
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

    # rysowanie linii
    if len(punkty) > 1:
        kolor = "red" if (suma_kg>MAX_KG or suma_ldm>MAX_LDM) else "green"
        folium.PolyLine(punkty, color=kolor, weight=4, opacity=0.7).add_to(m)

st_folium(m, width=1000, height=600)
