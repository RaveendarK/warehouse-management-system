# Warehouse Management System (Flask) - PostgreSQL version

## What I changed
- Switched database backend to PostgreSQL (using `psycopg2-binary`).
- App reads database URL from environment variable `DATABASE_URL` or uses a placeholder connection string.
- Interactive UI: Product and Movements lists use DataTables; select fields enhanced with Select2.
- Realistic sample data (laptops, monitors, keyboards, mobile phones, printers) and real warehouse locations.
- `create_sample_data.py` will populate the DB with sample products, locations and movements.

## Quick start (local)
1. Create virtualenv and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # on Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```
2. Ensure PostgreSQL is running and you have a database. Example connection string:
   `postgresql://username:password@localhost:5432/warehouse_db`
   Set it as environment variable:
   ```bash
   export DATABASE_URL='postgresql://username:password@localhost:5432/warehouse_db'
   ```
   On Windows PowerShell use: `$env:DATABASE_URL='postgresql://username:password@localhost:5432/warehouse_db'`
3. Create sample data:
   ```bash
   python create_sample_data.py
   ```
4. Run the app:
   ```bash
   python app.py
   ```
5. Open http://127.0.0.1:5000/

## Notes
- `create_sample_data.py` uses `create_all()`; for production use migrations (Flask-Migrate) instead.
- The app will fall back to a placeholder DB URL if `DATABASE_URL` is not set. Replace with your credentials.
<img width="1828" height="954" alt="Output-4" src="https://github.com/user-attachments/assets/ae9e2bcc-8410-4e1b-9f41-f1dbbb33c1c5" />
<img width="1826" height="960" alt="Output-3" src="https://github.com/user-attachments/assets/aff4afa1-e6e4-4a77-a3cf-f83e9162d0db" />
<img width="1829" height="963" alt="Output-2" src="https://github.com/user-attachments/assets/2eddbc05-e654-46d0-8e04-757be4f3dab0" />
<img width="1831" height="965" alt="Output-1" src="https://github.com/user-attachments/assets/85b0d14e-2c99-4a9e-8462-e91a340a360e" />

- 
