from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'nexus_gaming_secret_2024'

DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')

GAME_ICONS = {
    'VALORANT': '🎯',
    'PUBG MOBILE': '🔫',
    'FIFA 24': '⚽',
    'FREE FIRE': '🔥',
    'CALL OF DUTY': '💥',
    'MORTAL KOMBAT': '⚔️',
}

def get_db():
    """Database connectivity open karne ka helper function."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Application schemas tables initialize aur data seed karne ke liye."""
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS tournaments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_name TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                prize_pool TEXT NOT NULL,
                rules TEXT NOT NULL,
                max_teams INTEGER DEFAULT 32,
                format TEXT DEFAULT 'Team',
                status TEXT DEFAULT 'upcoming'
            );

            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                game TEXT NOT NULL,
                team_name TEXT,
                players_count INTEGER NOT NULL,
                tournament_id INTEGER,
                registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
            );
        ''')

        # Agar database empty ho toh default datasets inject karein
        count = conn.execute('SELECT COUNT(*) FROM tournaments').fetchone()[0]
        if count == 0:
            tournaments_data = [
                ('VALORANT', '2024-07-15', '18:00', '$5,000', '5v5 tactical shooter. No cheats, no macros. All accounts must be Gold rank or above. Best of 3 rounds per match.', 32, 'Team', 'upcoming'),
                ('PUBG MOBILE', '2024-07-20', '20:00', '$3,500', 'Squad mode only. 4 players per team. Custom room matches. Top 10 teams qualify for finals.', 64, 'Team', 'upcoming'),
                ('FIFA 24', '2024-07-25', '16:00', '$2,000', 'Solo tournament. 1v1 matches. Best of 3 per round. No custom tactics exploits allowed.', 16, 'Solo', 'upcoming'),
                ('FREE FIRE', '2024-08-01', '19:00', '$4,000', 'Squad of 4. Battle Royale format. Top 5 squads advance. No emulator allowed.', 48, 'Team', 'upcoming'),
                ('CALL OF DUTY', '2024-08-10', '21:00', '$6,000', '5v5 Multiplayer. Hardpoint + S&D format. No boosting. Must be Level 50+.', 32, 'Team', 'upcoming'),
                ('MORTAL KOMBAT', '2024-08-18', '17:00', '$1,500', 'Solo 1v1. Double elimination bracket. No DLC-exclusive moves in group stage.', 24, 'Solo', 'upcoming'),
            ]
            conn.executemany(
                'INSERT INTO tournaments (game_name, date, time, prize_pool, rules, max_teams, format, status) VALUES (?,?,?,?,?,?,?,?)',
                tournaments_data
            )
            conn.commit()

# Ensure tables are built smoothly before routing operations trigger
init_db()

# ----------------- APP ROUTES -----------------

@app.route('/')
def home():
    """Website Landing page control point."""
    with get_db() as conn:
        tournaments = conn.execute(
            "SELECT * FROM tournaments WHERE status='upcoming' ORDER BY date ASC LIMIT 6"
        ).fetchall()
        total_registrations = conn.execute('SELECT COUNT(*) FROM registrations').fetchone()[0]
        total_tournaments = conn.execute('SELECT COUNT(*) FROM tournaments').fetchone()[0]
    return render_template('index.html', tournaments=tournaments, icons=GAME_ICONS,
                           total_registrations=total_registrations, total_tournaments=total_tournaments)

@app.route('/tournaments')
def tournaments():
    """All tournaments listing with filter controls handling."""
    search = request.args.get('search', '')
    game_filter = request.args.get('game', '')
    with get_db() as conn:
        query = "SELECT * FROM tournaments WHERE 1=1"
        params = []
        if search:
            query += " AND game_name LIKE ?"
            params.append(f'%{search}%')
        if game_filter:
            query += " AND game_name = ?"
            params.append(game_filter)
        query += " ORDER BY date ASC"
        
        all_tournaments = conn.execute(query, params).fetchall()
        games = conn.execute('SELECT DISTINCT game_name FROM tournaments').fetchall()
    
    # Custom safety fallback checking: Agar standalone templates missing hon toh index par load karein
    try:
        return render_template('tournaments.html', tournaments=all_tournaments,
                               icons=GAME_ICONS, games=games, search=search, game_filter=game_filter)
    except Exception:
        return render_template('index.html', tournaments=all_tournaments, icons=GAME_ICONS,
                               total_registrations=len(all_tournaments), total_tournaments=len(games))

@app.route('/tournament/<int:tid>')
def tournament_detail(tid):
    """Specific single entry viewing handler."""
    with get_db() as conn:
        t = conn.execute('SELECT * FROM tournaments WHERE id=?', (tid,)).fetchone()
        if not t:
            flash('Tournament not found.', 'error')
            return redirect(url_for('tournaments'))
        reg_count = conn.execute(
            'SELECT COUNT(*) FROM registrations WHERE tournament_id=?', (tid,)
        ).fetchone()[0]
    return render_template('tournament_detail.html', t=t, icons=GAME_ICONS, reg_count=reg_count)

@app.route('/register')
def register():
    """Registration UI entry loader logic."""
    tid = request.args.get('tournament_id', '')
    with get_db() as conn:
        all_tournaments = conn.execute(
            "SELECT * FROM tournaments WHERE status='upcoming' ORDER BY date ASC"
        ).fetchall()
        selected = None
        if tid:
            selected = conn.execute('SELECT * FROM tournaments WHERE id=?', (tid,)).fetchone()
    return render_template('register.html', tournaments=all_tournaments,
                           selected=selected, icons=GAME_ICONS)

@app.route('/submit', methods=['POST'])
def submit():
    """Registrations context pipeline processor entry endpoint."""
    player_name = request.form.get('player_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    game = request.form.get('game', '').strip()
    team_name = request.form.get('team_name', '').strip()
    players_count = request.form.get('players_count', '1')
    tournament_id = request.form.get('tournament_id', None)

    errors = []
    if not player_name: errors.append('Player name is required.')
    if not email or '@' not in email: errors.append('Valid email is required.')
    if not phone or len(phone) < 10: errors.append('Valid phone number is required.')
    if not game: errors.append('Please select a game.')

    if errors:
        for e in errors:
            flash(e, 'error')
        return redirect(url_for('register', tournament_id=tournament_id or ''))

    try:
        players_count = int(players_count)
    except ValueError:
        players_count = 1

    with get_db() as conn:
        if tournament_id and tournament_id != "":
            dup = conn.execute(
                'SELECT id FROM registrations WHERE email=? AND tournament_id=?',
                (email, tournament_id)
            ).fetchone()
            if dup:
                flash('This email is already registered for this tournament.', 'error')
                return redirect(url_for('register', tournament_id=tournament_id))

        conn.execute(
            'INSERT INTO registrations (player_name, email, phone, game, team_name, players_count, tournament_id) VALUES (?,?,?,?,?,?,?)',
            (player_name, email, phone, game, team_name, players_count, tournament_id if tournament_id != "" else None)
        )
        conn.commit()

    flash(f'🎮 Registration successful! Welcome to the arena, {player_name}!', 'success')
    return redirect(url_for('success', name=player_name, game=game))

@app.route('/success')
def success():
    """Registration confirmation dynamic screen dispatcher."""
    name = request.args.get('name', 'Player')
    game = request.args.get('game', '')
    return render_template('success.html', name=name, game=game, icons=GAME_ICONS)

@app.route('/admin')
def admin():
    """Full database overview dashboard engine controls panel."""
    with get_db() as conn:
        all_registrations = conn.execute(
            '''SELECT r.*, t.game_name as tournament_name 
               FROM registrations r 
               LEFT JOIN tournaments t ON r.tournament_id = t.id 
               ORDER BY r.registered_at DESC'''
        ).fetchall()
        all_tournaments = conn.execute('SELECT * FROM tournaments ORDER BY date ASC').fetchall()
        stats = {
            'total_reg': conn.execute('SELECT COUNT(*) FROM registrations').fetchone()[0],
            'total_t': conn.execute('SELECT COUNT(*) FROM tournaments').fetchone()[0],
            'upcoming': conn.execute("SELECT COUNT(*) FROM tournaments WHERE status='upcoming'").fetchone()[0],
        }
    return render_template('admin.html', registrations=all_registrations,
                           tournaments=all_tournaments, stats=stats, icons=GAME_ICONS)

@app.route('/add_tournament', methods=['POST'])
def add_tournament():
    """Endpoint processor to create a tournament securely."""
    game_name = request.form.get('game_name', '').strip()
    date = request.form.get('date', '').strip()
    time = request.form.get('time', '').strip()
    prize_pool = request.form.get('prize_pool', '').strip()
    rules = request.form.get('rules', '').strip()
    max_teams = request.form.get('max_teams', 32)
    fmt = request.form.get('format', 'Team')

    if not all([game_name, date, time, prize_pool, rules]):
        flash('All fields are required.', 'error')
        return redirect(url_for('admin'))

    with get_db() as conn:
        conn.execute(
            'INSERT INTO tournaments (game_name, date, time, prize_pool, rules, max_teams, format) VALUES (?,?,?,?,?,?,?)',
            (game_name, date, time, prize_pool, rules, int(max_teams), fmt)
        )
        conn.commit()

    flash(f'Tournament "{game_name}" added successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/delete/<int:tid>')
def delete_tournament(tid):
    """Specific entry destruction pipeline engine."""
    with get_db() as conn:
        t = conn.execute('SELECT game_name FROM tournaments WHERE id=?', (tid,)).fetchone()
        if t:
            conn.execute('DELETE FROM registrations WHERE tournament_id=?', (tid,))
            conn.execute('DELETE FROM tournaments WHERE id=?', (tid,))
            conn.commit()
            flash(f'Tournament "{t["game_name"]}" deleted.', 'success')
        else:
            flash('Tournament not found.', 'error')
    return redirect(url_for('admin'))

@app.route('/delete_registration/<int:rid>')
def delete_registration(rid):
    """Specific team registration context drop action entry."""
    with get_db() as conn:
        conn.execute('DELETE FROM registrations WHERE id=?', (rid,))
        conn.commit()
    flash('Registration removed.', 'success')
    return redirect(url_for('admin'))

@app.route('/api/tournaments')
def api_tournaments():
    """Public JSON array format provider entry endpoint."""
    with get_db() as conn:
        ts = conn.execute("SELECT * FROM tournaments WHERE status='upcoming' ORDER BY date ASC").fetchall()
    return jsonify([dict(t) for t in ts])

if __name__ == '__main__':
    app.run(debug=True, port=5000)