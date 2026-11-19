# South African Battery Finder Pro

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Run `pip install -r requirements.txt`.
4. Run `streamlit run app.py`.

## Files
- `app.py`: Streamlit web application.
- `battery_database.csv`: starter fitment database.

## Important data note
The included Volkswagen Polo row is an illustrative example only. It is deliberately marked unverified and its brand codes are placeholders. Do not use it to recommend or sell a battery. Replace it with fitment records confirmed from licensed/manufacturer/supplier catalogues and vehicle-specific checks.

## Features
- Search by year, make, model, engine and fuel.
- Reverse lookup by South African battery size code, DIN size, Willard, First Battery Centre, Exide, Bosch or Varta code.
- Displays Ah, CCA, voltage, technology, start-stop, dimensions and terminal layout.
- Admin form to add records; CSV import/export.

## VIN / registration lookup
Not implemented: it requires a licensed South African registration/VIN data provider and an appropriate vehicle fitment catalogue. The app does not guess fitments.
