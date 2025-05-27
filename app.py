import streamlit as st
import pandas as pd

# 1) Konfiguracja
vehicles = ["TK227CK","TK742AG","ESI461A","ESI4217","TK654CH","TK564CH","OP4556U","SB4432V"]
days     = ["Poniedziałek","Wtorek","Środa","Czwartek","Piątek","Sobota","Niedziela"]
slots    = 5  # 5 pod-wierszy

# Przechowujemy dane w session_state jako słownik pojazd → DataFrame 
if "vehicle_events" not in st.session_state:
    st.session_state.vehicle_events = {
        v: pd.DataFrame({
            "Day": [""]*slots,
            "City": [""]*slots,
            "Masa": [""]*slots,
            "LDM": [""]*slots,
            "Type": [""]*slots,
        }) for v in vehicles
    }

st.title("📋 Harmonogram zdarzeń dla pojazdów")

# 2) Renderujemy expandery—pojazd → jego 5-wierszowa tabela
for v in vehicles:
    df_v = st.session_state.vehicle_events[v]
    with st.expander(f"🚚 {v}", expanded=False):
        edited = st.data_editor(
            df_v,
            num_rows="fixed",
            use_container_width=True,
            key=f"ed_{v}"
        )
        st.session_state.vehicle_events[v] = edited

# Teraz zbieramy wszystkie zdarzenia w jeden DataFrame
all_events = []
for v, df_v in st.session_state.vehicle_events.items():
    df = df_v.copy()
    df["Vehicle"] = v
    all_events.append(df)
combined = pd.concat(all_events, ignore_index=True)

st.subheader("✅ Wszystkie zdarzenia")
st.dataframe(combined)

# 3) (w kolejnym kroku) – na bazie `combined` możesz zbudować mapę
#    filtrujesz combined.dropna(subset=["City","Day"]), geokodujesz i rysujesz trasę
