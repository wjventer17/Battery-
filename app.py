import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="South African Battery Finder Pro", page_icon="🔋", layout="wide")

DB = Path(__file__).with_name("battery_database.csv")
COLUMNS = [
    "year", "make", "model", "engine", "fuel", "ah", "cca", "voltage",
    "sa_size", "din_size", "length_mm", "width_mm", "height_mm",
    "terminal_layout", "technology", "start_stop",
    "willard_code", "fbc_code", "exide_code", "bosch_code", "varta_code",
    "verified", "source", "notes"
]

SAMPLE = [{
    "year": 2024, "make": "Volkswagen", "model": "Polo", "engine": "1.6",
    "fuel": "Petrol", "ah": 60, "cca": 540, "voltage": 12,
    "sa_size": "652C", "din_size": "", "length_mm": "", "width_mm": "",
    "height_mm": "", "terminal_layout": "", "technology": "To verify",
    "start_stop": "To verify", "willard_code": "VERIFY",
    "fbc_code": "VERIFY", "exide_code": "VERIFY", "bosch_code": "VERIFY",
    "varta_code": "VERIFY", "verified": "No", "source": "",
    "notes": "Illustrative record only. Confirm fitment and all specifications before use."
}]

def load_db():
    if not DB.exists():
        pd.DataFrame(SAMPLE, columns=COLUMNS).to_csv(DB, index=False)
    df = pd.read_csv(DB, dtype=str).fillna("")
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[COLUMNS]

def save_db(df):
    df[COLUMNS].fillna("").to_csv(DB, index=False)

def contains(series, value):
    return series.astype(str).str.contains(str(value).strip(), case=False, na=False, regex=False)

df = load_db()

st.title("🔋 South African Battery Finder Pro")
st.caption("Vehicle-to-battery fitment lookup | South African size codes and brand cross-references")
st.info("Fitment data must be confirmed against a trusted catalogue, VIN, vehicle equipment and the battery currently fitted. Sample data is illustrative and is not a fitment recommendation.")

tab_vehicle, tab_code, tab_admin, tab_about = st.tabs(
    ["🚗 Vehicle search", "🔎 Battery code search", "🛠️ Admin / database", "ℹ️ About"]
)

with tab_vehicle:
    st.subheader("Find a battery by vehicle")
    a, b, c, d = st.columns(4)
    years = sorted([x for x in df.year.unique() if x], reverse=True)
    makes = sorted([x for x in df.make.unique() if x])
    with a:
        year = st.selectbox("Year (optional)", ["Any"] + years)
    with b:
        make = st.selectbox("Make (optional)", ["Any"] + makes)
    with c:
        models = sorted(df[df.make.eq(make)].model.unique()) if make != "Any" else sorted(df.model.unique())
        model = st.selectbox("Model (optional)", ["Any"] + [x for x in models if x])
    with d:
        engine = st.text_input("Engine (optional)", placeholder="e.g. 1.6, 2.0 TDI")
    fuel = st.selectbox("Fuel type (optional)", ["Any", "Petrol", "Diesel", "Hybrid", "Electric", "Other"])

    results = df.copy()
    if year != "Any": results = results[results.year.eq(year)]
    if make != "Any": results = results[results.make.eq(make)]
    if model != "Any": results = results[results.model.eq(model)]
    if engine.strip(): results = results[contains(results.engine, engine)]
    if fuel != "Any": results = results[results.fuel.str.casefold().eq(fuel.casefold())]

    if st.button("Find matching batteries", type="primary"):
        st.session_state["vehicle_results"] = results
    if "vehicle_results" in st.session_state:
        results = st.session_state["vehicle_results"]
        if results.empty:
            st.warning("No matching records. Try fewer filters or add a verified fitment in Admin.")
        else:
            st.success(f"{len(results)} matching database record(s)")
            for idx, row in results.iterrows():
                title = f'{row.year} {row.make} {row.model} {row.engine}'.strip()
                with st.expander(title, expanded=True):
                    if row.verified.lower() == "yes":
                        st.success("Database record marked verified")
                    else:
                        st.warning("UNVERIFIED — confirm before recommending or selling")
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("South African size", row.sa_size or "Not listed")
                    m2.metric("Capacity", f'{row.ah} Ah' if row.ah else "Not listed")
                    m3.metric("CCA", row.cca or "Not listed")
                    m4.metric("Voltage", f'{row.voltage} V' if row.voltage else "Not listed")
                    codes = pd.DataFrame([
                        ["Willard", row.willard_code], ["First Battery Centre", row.fbc_code],
                        ["Exide", row.exide_code], ["Bosch", row.bosch_code],
                        ["Varta", row.varta_code], ["DIN / equivalent size", row.din_size]
                    ], columns=["Brand / system", "Code"])
                    st.markdown("**Battery codes and equivalents**")
                    st.dataframe(codes, hide_index=True, use_container_width=True)
                    details = {
                        "Technology": row.technology, "Start-stop": row.start_stop,
                        "Terminal layout": row.terminal_layout,
                        "Dimensions (L × W × H)": " × ".join(
                            [str(v) for v in [row.length_mm, row.width_mm, row.height_mm] if v]
                        ) + (" mm" if any([row.length_mm, row.width_mm, row.height_mm]) else "Not listed"),
                        "Fuel": row.fuel, "Source": row.source, "Notes": row.notes
                    }
                    st.table(pd.DataFrame(details.items(), columns=["Specification", "Value"]))

with tab_code:
    st.subheader("Reverse lookup by battery size or brand code")
    search_code = st.text_input("Enter a code", placeholder="e.g. 652C or a Willard / FBC code")
    if search_code:
        mask = pd.Series(False, index=df.index)
        code_cols = ["sa_size", "din_size", "willard_code", "fbc_code",
                     "exide_code", "bosch_code", "varta_code"]
        for col in code_cols:
            mask |= contains(df[col], search_code)
        found = df[mask]
        if found.empty:
            st.warning("No matching battery code found in the current database.")
        else:
            st.success(f"{len(found)} matching vehicle record(s)")
            show_cols = ["year", "make", "model", "engine", "sa_size", "ah", "cca",
                         "willard_code", "fbc_code", "exide_code", "bosch_code", "varta_code", "verified"]
            st.dataframe(found[show_cols], hide_index=True, use_container_width=True)

with tab_admin:
    st.subheader("Add or maintain fitment records")
    st.write("Only enter codes and specifications supported by a reliable supplier or manufacturer catalogue.")
    with st.form("add_record"):
        x1, x2, x3, x4 = st.columns(4)
        with x1:
            new_year = st.text_input("Year")
            new_make = st.text_input("Make")
            new_model = st.text_input("Model")
            new_engine = st.text_input("Engine")
            new_fuel = st.selectbox("Fuel", ["Petrol", "Diesel", "Hybrid", "Electric", "Other"])
        with x2:
            new_sa = st.text_input("South African size code", placeholder="e.g. 652C")
            new_din = st.text_input("DIN / equivalent size")
            new_ah = st.text_input("Ah")
            new_cca = st.text_input("CCA")
            new_voltage = st.text_input("Voltage", value="12")
        with x3:
            new_willard = st.text_input("Willard code")
            new_fbc = st.text_input("First Battery Centre code")
            new_exide = st.text_input("Exide code")
            new_bosch = st.text_input("Bosch code")
            new_varta = st.text_input("Varta code")
        with x4:
            new_tech = st.selectbox("Technology", ["Standard", "EFB", "AGM", "Gel", "Lithium", "To verify"])
            new_ss = st.selectbox("Start-stop", ["Yes", "No", "To verify"])
            new_len = st.text_input("Length (mm)")
            new_wid = st.text_input("Width (mm)")
            new_hgt = st.text_input("Height (mm)")
        new_term = st.text_input("Terminal layout")
        new_verified = st.selectbox("Fitment verified?", ["No", "Yes"])
        new_source = st.text_input("Source / catalogue reference")
        new_notes = st.text_area("Notes")
        submitted = st.form_submit_button("Save battery fitment", type="primary")
        if submitted:
            if not all([new_year, new_make, new_model, new_engine, new_sa]):
                st.error("Year, make, model, engine and South African size code are required.")
            else:
                record = dict.fromkeys(COLUMNS, "")
                record.update({
                    "year": new_year, "make": new_make, "model": new_model,
                    "engine": new_engine, "fuel": new_fuel, "sa_size": new_sa,
                    "din_size": new_din, "ah": new_ah, "cca": new_cca,
                    "voltage": new_voltage, "willard_code": new_willard,
                    "fbc_code": new_fbc, "exide_code": new_exide,
                    "bosch_code": new_bosch, "varta_code": new_varta,
                    "technology": new_tech, "start_stop": new_ss,
                    "length_mm": new_len, "width_mm": new_wid, "height_mm": new_hgt,
                    "terminal_layout": new_term, "verified": new_verified,
                    "source": new_source, "notes": new_notes
                })
                df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
                save_db(df)
                st.success("Fitment record saved.")
                st.rerun()

    st.markdown("**Current database**")
    st.dataframe(df, use_container_width=True, hide_index=True)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download database CSV", csv_bytes, "battery_database.csv", "text/csv")
    uploaded = st.file_uploader("Import a completed battery database CSV", type=["csv"])
    if uploaded and st.button("Replace database with uploaded CSV"):
        incoming = pd.read_csv(uploaded, dtype=str).fillna("")
        missing = [c for c in COLUMNS if c not in incoming.columns]
        if missing:
            st.error("CSV is missing columns: " + ", ".join(missing))
        else:
            save_db(incoming[COLUMNS])
            st.success("Database imported.")
            st.rerun()

with tab_about:
    st.subheader("How this app works")
    st.markdown("""
    - **Vehicle search:** filters the local fitment database by year, make, model, engine and fuel.
    - **Battery code search:** searches South African size codes and brand cross-reference fields.
    - **Admin:** add verified fitments and import/export the CSV database.
    - **Verification:** each record has a verification flag and source field.

    This app does not automatically identify vehicles from a registration number or VIN.
    That requires a licensed South African vehicle data / VIN lookup provider and a fitment
    catalogue with the required coverage. Do not infer fitment from a battery code alone.
    """)
    st.caption(f"Database file: {DB.name} | Records: {len(df)}")

st.divider()
st.caption("Battery Finder Pro • South Africa • Always verify polarity, hold-down, dimensions, terminal type, required technology and manufacturer fitment.")
