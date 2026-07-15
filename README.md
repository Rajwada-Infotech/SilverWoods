# SILVERWOODS

A premium real estate website for the **Silverwoods Villa Community** — South Jagaddal, Kolkata. Built with Django + Tailwind CSS + Three.js.

---

## Tech Stack

- **Backend** — Django 5.x, SQLite
- **Frontend** — Tailwind CSS, Alpine.js, GSAP
- **3D Viewer** — Three.js + OrbitControls
- **Icons** — Font Awesome

---

## How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Rajwada-Infotech/SILVERWOODS.git
cd SILVERWOODS
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (admin login)

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Then open **http://127.0.0.1:8000** in your browser.

---

## Pages

| URL | Description |
|-----|-------------|
| `/` | Landing page (Hero, About, Amenities, Pricing, Contact) |
| `/brochure/` | Interactive brochure viewer |
| `/blueprint/` | 3D site plan viewer |
| `/plots/` | Plot metrics & availability map |
| `/admin-panel/` | Custom admin dashboard |

---

## Admin Panel

Login at `/admin-panel/login/` with the superuser credentials you created.

Features:
- **Dashboard** — leads, queries, popup stats
- **Pricing** — manage flat types and prices
- **Leads** — view and export enquiries
- **Popup Ads** — create and manage popup advertisements
- **Plot Metrics** — update villa plot status (Available / Sold / Reserved)
- **Profile** — update admin account details

---

## Notes

- Media files (uploaded images) are stored in the `media/` folder and are excluded from git.
- The database (`db.sqlite3`) is excluded from git — run migrations on each new setup.
- For production, update `SECRET_KEY`, `DEBUG = False`, and configure `ALLOWED_HOSTS` in `silverwoods/settings.py`.
