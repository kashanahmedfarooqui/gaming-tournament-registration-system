# 🎮 NEXUS ARENA — Gaming Tournament Registration System

A full-stack web app for managing gaming tournaments, built with Flask + SQLite + vanilla JS.

## Tech Stack
- **Backend**: Python / Flask
- **Database**: SQLite (auto-created on first run)
- **Frontend**: HTML5, CSS3 (custom), JavaScript (vanilla)
- **Fonts**: Orbitron + Rajdhani (Google Fonts)

## Setup & Run

```bash
# 1. Navigate to project folder
cd tournament_app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py

# 4. Open in browser
# http://localhost:5000
```

## Pages
| Route | Description |
|-------|-------------|
| `/` | Home page with hero + featured tournaments |
| `/tournaments` | Browse all tournaments with search/filter |
| `/tournament/<id>` | Tournament detail with countdown timer |
| `/register` | Player/team registration form |
| `/admin` | Admin dashboard (manage tournaments + registrations) |

## Features
- Dark neon gaming theme (Orbitron font, green/cyan accents)
- Animated grid background + scanline effect
- Live countdown timers on every tournament card
- Registration form with client + server-side validation
- Duplicate registration detection per tournament
- Admin: add/delete tournaments, remove registrations
- Live search in admin registrations table
- Responsive — works on mobile + desktop
- Stat counter animations on home page

## Database
Auto-initialized with 6 seed tournaments on first run.
- `tournaments` table: game_name, date, time, prize_pool, rules, max_teams, format, status
- `registrations` table: player details + tournament FK

## Project Structure
```
tournament_app/
├── app.py              ← Flask app + routes + DB logic
├── database.db         ← SQLite DB (auto-created)
├── requirements.txt
├── templates/
│   ├── base.html       ← Shared layout + nav + flash
│   ├── index.html      ← Home page
│   ├── tournaments.html
│   ├── tournament_detail.html
│   ├── register.html
│   ├── success.html
│   └── admin.html
└── static/
    ├── css/style.css   ← All styles
    └── js/main.js      ← Shared JS
```
