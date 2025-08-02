# Dealroom Tool - Setup Anweisungen

## Projekt-Initialisierung

Das Django-Projekt wurde erfolgreich initialisiert! Hier sind die wichtigsten Informationen:

### ✅ Bereits durchgeführt:
- ✅ Virtuelles Environment erstellt (`venv/`)
- ✅ Alle Abhängigkeiten installiert (`requirements.txt`)
- ✅ Django-Migrationen ausgeführt
- ✅ Datenbank initialisiert (`db.sqlite3`)
- ✅ Superuser erstellt (Username: `admin`, Email: `admin@example.com`)
- ✅ Statische Dateien gesammelt
- ✅ Django-Entwicklungsserver gestartet

### 🚀 Server läuft auf:
- **Hauptanwendung**: http://127.0.0.1:8000/
- **Admin-Interface**: http://127.0.0.1:8000/admin/
- **Dealrooms**: http://127.0.0.1:8000/dealrooms/
- **Benutzer**: http://127.0.0.1:8000/users/

### 🔑 Admin-Zugang:
- **Username**: admin
- **Email**: admin@example.com
- **Passwort**: (wird beim ersten Login gesetzt)

### 📁 Projektstruktur:
```
DealroomTool/
├── core/                 # Haupt-App (Dashboard, About, etc.)
├── deals/               # Dealroom-Verwaltung
├── users/               # Benutzer-Verwaltung
├── generator/           # Generator für Landing Pages
├── dealroom_dashboard/  # Django-Projekt-Einstellungen
├── templates/           # HTML-Templates
├── static/             # CSS, JS, Bilder
└── venv/               # Virtuelles Environment
```

### 🛠️ Nützliche Befehle:

**Virtuelles Environment aktivieren:**
```bash
source venv/bin/activate
```

**Django-Server starten:**
```bash
python manage.py runserver
```

**Neue Migrationen erstellen:**
```bash
python manage.py makemigrations
```

**Migrationen anwenden:**
```bash
python manage.py migrate
```

**Superuser erstellen:**
```bash
python manage.py createsuperuser
```

**Statische Dateien sammeln:**
```bash
python manage.py collectstatic
```

### 🔧 Umgebungsvariablen:
Das Projekt verwendet `python-decouple` für Umgebungsvariablen. Erstellen Sie eine `.env` Datei im Projektroot:

```env
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
```

### 📝 Nächste Schritte:
1. Öffnen Sie http://127.0.0.1:8000/ im Browser
2. Melden Sie sich im Admin-Interface an (http://127.0.0.1:8000/admin/)
3. Setzen Sie das Admin-Passwort beim ersten Login
4. Erstellen Sie erste Dealrooms über das Admin-Interface
5. Testen Sie die Generator-Funktionen

### 🐛 Troubleshooting:
- Falls der Server nicht startet, prüfen Sie ob Port 8000 frei ist
- Bei Import-Fehlern: Stellen Sie sicher, dass das virtuelle Environment aktiviert ist
- Bei Datenbank-Fehlern: Führen Sie `python manage.py migrate` erneut aus

Das Projekt ist jetzt bereit für die Entwicklung! 🎉 