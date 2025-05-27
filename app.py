import streamlit as st
import pandas as pd

# konfiguracja
vehicles = ["TK227CK","TK742AG","ESI461A","ESI4217","TK654CH","TK564CH","OP4556U","SB4432V"]
days = ["Poniedziałek","Wtorek","Środa","Czwartek","Piątek","Sobota","Niedziela"]
slots = range(1,6)

# budowa kolumn
cols = ["Vehicle"]
for d in days:
    for s in slots:
        cols += [f"{d}#{s}_Miejsce", f"{d}#{s}_Z/R", f"{d}#{s}_Masa", f"{d}#{s}_LDM"]

# inicjalizacja
if "df" not in st.session_state:
    data = []
    for v in vehicles:
        row = {"Vehicle": v}
        for c in cols[1:]:
            row[c] = ""
        data.append(row)
    st.session_state.df = pd.DataFrame(data, columns=cols)

df = st.session_state.df
# edycja
edited = st.data_editor(df, use_container_width=True, num_rows="fixed", key="tabela")
st.session_state.df = edited
