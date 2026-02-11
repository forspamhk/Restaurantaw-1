import streamlit as st
import pandas as pd

st.set_page_config(page_title="Restaurantauswertung", layout="wide")
st.title("📊 Tägliche Restaurantauswertung")

uploaded_file = st.file_uploader("Excel-Datei hochladen (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        # Excel einlesen
        df = pd.read_excel(uploaded_file)

        # Spaltennamen standardisieren (falls Tippfehler oder Leerzeichen)
        df.columns = [c.strip().replace(" ", "_") for c in df.columns]

        # Zahlen sauber konvertieren (Text → Zahl)
        numeric_cols = [
            "Umsatz_Speisen", "Umsatz_Getraenke", 
            "EK_Speisen", "EK_Getraenke", 
            "Personal_Service", "Personal_Kueche", 
            "Stunden", "Gaeste"
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            else:
                st.warning(f"Spalte {col} fehlt in der Excel! Wird mit 0 gefüllt.")
                df[col] = 0

        # Datum sauber konvertieren
        if "Datum" in df.columns:
            df["Datum"] = pd.to_datetime(df["Datum"], errors="coerce")
        else:
            st.error("Spalte 'Datum' fehlt!")
            st.stop()

        # Berechnungen
        df["Gesamtumsatz"] = df["Umsatz_Speisen"] + df["Umsatz_Getraenke"]

        df["Wareneinsatz_Speisen"] = df["Umsatz_Speisen"] - df["EK_Speisen"]
        df["Wareneinsatz_Getraenke"] = df["Umsatz_Getraenke"] - df["EK_Getraenke"]

        df["Wareneinsatz_%_Speisen"] = df.apply(
            lambda x: (x["EK_Speisen"]/x["Umsatz_Speisen"]*100) if x["Umsatz_Speisen"]>0 else 0, axis=1)
        df["Wareneinsatz_%_Getraenke"] = df.apply(
            lambda x: (x["EK_Getraenke"]/x["Umsatz_Getraenke"]*100) if x["Umsatz_Getraenke"]>0 else 0, axis=1)

        df["Personal_Gesamt"] = df["Personal_Service"] + df["Personal_Kueche"]
        df["Personalkosten_%"] = df.apply(
            lambda x: (x["Personal_Gesamt"]/x["Gesamtumsatz"]*100) if x["Gesamtumsatz"]>0 else 0, axis=1)

        df["Umsatz_pro_Stunde"] = df.apply(
            lambda x: (x["Gesamtumsatz"]/x["Stunden"]) if x["Stunden"]>0 else 0, axis=1)
        df["Umsatz_pro_Gast"] = df.apply(
            lambda x: (x["Gesamtumsatz"]/x["Gaeste"]) if x["Gaeste"]>0 else 0, axis=1)

        df["Deckungsbeitrag"] = df["Wareneinsatz_Speisen"] + df["Wareneinsatz_Getraenke"]
        df["Betriebsergebnis"] = df["Deckungsbeitrag"] - df["Personal_Gesamt"]

        # Tagesübersicht
        st.subheader("📅 Tagesübersicht")
        st.dataframe(df.round(2))

        # Monatsauswertung
        df["Monat"] = df["Datum"].dt.to_period("M")
        monat = df.groupby("Monat").sum(numeric_only=True)
        st.subheader("📈 Monatsübersicht")
        st.dataframe(monat.round(2))

        # Optional: Diagramm
        st.subheader("💹 Umsatz Verlauf")
        st.line_chart(df.set_index("Datum")[["Gesamtumsatz", "Umsatz_Speisen", "Umsatz_Getraenke"]])

    except Exception as e:
        st.error(f"Fehler beim Verarbeiten der Excel-Datei: {e}")

