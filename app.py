import streamlit as st
import pandas as pd

st.set_page_config(page_title="Restaurantauswertung", layout="wide")

st.title("📊 Restaurantauswertung")

uploaded_file = st.file_uploader("Excel-Datei hochladen", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)
    df["Datum"] = pd.to_datetime(df["Datum"])

    # Umsätze
    df["Gesamtumsatz"] = df["Umsatz_Speisen"] + df["Umsatz_Getraenke"]

    # Wareneinsatz
    df["Wareneinsatz_Speisen"] = df["Umsatz_Speisen"] - df["EK_Speisen"]
    df["Wareneinsatz_Getraenke"] = df["Umsatz_Getraenke"] - df["EK_Getraenke"]

    df["Wareneinsatz_%_Speisen"] = df["EK_Speisen"] / df["Umsatz_Speisen"] * 100
    df["Wareneinsatz_%_Getraenke"] = df["EK_Getraenke"] / df["Umsatz_Getraenke"] * 100

    # Personal
    df["Personal_Gesamt"] = df["Personal_Service"] + df["Personal_Kueche"]
    df["Personalkosten_%"] = df["Personal_Gesamt"] / df["Gesamtumsatz"] * 100

    # Kennzahlen
    df["Umsatz_pro_Stunde"] = df["Gesamtumsatz"] / df["Stunden"]
    df["Umsatz_pro_Gast"] = df["Gesamtumsatz"] / df["Gaeste"]

    df["Deckungsbeitrag"] = df["Wareneinsatz_Speisen"] + df["Wareneinsatz_Getraenke"]
    df["Betriebsergebnis"] = df["Deckungsbeitrag"] - df["Personal_Gesamt"]

    st.subheader("Tagesübersicht")
    st.dataframe(df.round(2))

    # Monatsauswertung
    df["Monat"] = df["Datum"].dt.to_period("M")
    monat = df.groupby("Monat").sum(numeric_only=True)

    st.subheader("Monatsübersicht")
    st.dataframe(monat.round(2))
