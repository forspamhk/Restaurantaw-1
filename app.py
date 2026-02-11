import streamlit as st
import pandas as pd

st.set_page_config(page_title="Restaurantauswertung", layout="wide")
st.title("📊 Tägliche Restaurantauswertung")

uploaded_file = st.file_uploader("Excel-Datei hochladen (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        # Excel einlesen
        df = pd.read_excel(uploaded_file)
        # Spaltennamen standardisieren: Trim + Unterstrich statt Leerzeichen
        df.columns = [c.strip().replace(" ", "_") for c in df.columns]

        st.write("✅ Spalten in der Excel erkannt:", df.columns.tolist())

        # Liste aller benötigten Spalten
        required_cols = [
            "Datum", "Umsatz_Speisen", "Umsatz_Getraenke",
            "EK_Speisen", "EK_Getraenke",
            "Personal_Service", "Personal_Kueche",
            "Stunden", "Gaeste"
        ]

        # Fehlende Spalten automatisch erstellen
        for col in required_cols:
            if col not in df.columns:
                st.warning(f"Spalte '{col}' fehlt – wird automatisch mit 0 gefüllt")
                df[col] = 0

        # Zahlen sauber konvertieren
        numeric_cols = required_cols[1:]  # alle außer Datum
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Datum sauber konvertieren
        df["Datum"] = pd.to_datetime(df["Datum"], errors="coerce")
        if df["Datum"].isnull().all():
            st.error("Alle Werte in 'Datum' sind ungültig. Bitte prüfen!")
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

        # Monatsauswertung
        df["Monat"] = df["Datum"].dt.to_period("M")
        monat = df.groupby("Monat").sum(numeric_only=True)

        # --- KPI-Boxen für den letzten Tag ---
        last_day = df.iloc[-1]  # letzter Eintrag
        st.subheader(f"📅 Kennzahlen für {last_day['Datum'].date()}")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Gesamtumsatz", f"{last_day['Gesamtumsatz']:.2f} €")
        col2.metric("Wareneinsatz %", f"{((last_day['EK_Speisen']+last_day['EK_Getraenke'])/last_day['Gesamtumsatz']*100 if last_day['Gesamtumsatz']>0 else 0):.2f} %")
        col3.metric("Personalkosten %", f"{last_day['Personalkosten_%']:.2f} %")
        col4.metric("Betriebsergebnis", f"{last_day['Betriebsergebnis']:.2f} €")

        # Tagesübersicht
        st.subheader("📋 Tagesübersicht")
        st.dataframe(df.round(2))

        # Monatsübersicht
        st.subheader("📈 Monatsübersicht")
        st.dataframe(monat.round(2))

        # Umsatz Diagramm
        st.subheader("💹 Umsatz Verlauf")
        st.line_chart(df.set_index("Datum")[["Gesamtumsatz", "Umsatz_Speisen", "Umsatz_Getraenke"]])

    except Exception as e:
        st.error(f"Fehler beim Verarbeiten der Excel-Datei: {e}")
