<div align="center">
  <img src="static/images/logo.png" alt="Silverwoods Logo" width="180"/>

  # Silverwoods

  ### Premium Real Estate Platform — Silverwoods Villa Community, South Jagaddal, Kolkata

  Built with Django, Tailwind CSS, and Three.js

</div>

---

## Overview

Silverwoods is a full-featured real estate marketing and management platform for the **Silverwoods Villa Community**, a premium residential development in South Jagaddal, Kolkata. The platform combines a polished public-facing marketing site with an interactive 3D property viewer and a custom administrative dashboard for managing leads, pricing, and plot inventory.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.x, SQLite |
| Frontend | Tailwind CSS, Alpine.js, GSAP |
| 3D Visualization | Three.js (OrbitControls) |
| Icons | Font Awesome |

---

## Getting Started

### Prerequisites
- Python 3.10+
- pip
- git

### 1. Clone the repository
```bash
git clone https://github.com/Rajwada-Infotech/SilverWoods.git
cd SilverWoods
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply database migrations
```bash
python manage.py migrate
```

### 5. Create an administrator account
```bash
python manage.py createsuperuser
```

### 6. Start the development server
```bash
python manage.py runserver
```

The application will be available at **http://127.0.0.1:8000**.

---

## Application Pages

| Route | Description |
|---|---|
| `/` | Landing page — Hero, About, Amenities, Pricing, Contact |
| `/brochure/` | Interactive digital brochure viewer |
| `/blueprint/` | 3D site plan viewer |
| `/plots/` | Plot metrics and availability map |
| `/admin-panel/` | Custom administrative dashboard |

---

## Administrative Dashboard

Accessible at `/admin-panel/login/` using the superuser credentials created above.

**Capabilities:**
- **Dashboard** — Overview of leads, enquiries, and popup ad performance
- **Pricing** — Manage flat types and pricing tiers
- **Leads** — View and export customer enquiries
- **Popup Ads** — Create and manage promotional popups
- **Plot Metrics** — Update villa plot status (Available / Sold / Reserved)
- **Profile** — Manage administrator account details

---

## Configuration Notes

- Uploaded media files are stored in the `media/` directory and are excluded from version control.
- The local database (`db.sqlite3`) is excluded from version control; run migrations after cloning to initialize it.
- Before deploying to production, update the following in `silverwoods/settings.py`:
  - Set a new, secret `SECRET_KEY`
  - Set `DEBUG = False`
  - Configure `ALLOWED_HOSTS` appropriately

---

<div align="center">
  <sub>© Rajwada Infotech. All rights reserved.</sub>
</div>
