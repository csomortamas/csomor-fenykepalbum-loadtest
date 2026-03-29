# Fényképalbum Terheléspróba (Load Test)

Ez a projekt a **csomor-paas-fenykepalbum** automatikus skálázódásának tesztelésére szolgál.

## Projekt struktúra

```
csomor-fenykepalbum-loadtest/
├── locustfile.py      # Locust terheléspróba forgatókönyv
├── requirements.txt   # Python függőségek
├── Procfile          # Heroku process definíció
├── runtime.txt       # Python verzió
└── README.md         # Ez a fájl
```

## Locust terheléspróba

A `locustfile.py` két felhasználói típust definiál:

### 1. PhotoAlbumUser (normál felhasználó)
- Fotók listázása (leggyakoribb művelet)
- Egyedi fotó lekérése
- Főoldal betöltése
- Felhasználói státusz ellenőrzése
- Bejelentkezés/kijelentkezés ciklus
- Health check

### 2. HeavyLoadUser (intenzív terhelés)
- Gyors, egymás utáni kérések
- Minimális várakozási idő

## Lefedett funkciók

| Funkció | Endpoint | Leírás |
|---------|----------|--------|
| Fotólista | GET /api/photos | Lapozott fotólista lekérése |
| Fotó részlet | GET /api/photos/:id | Egyedi fotó lekérése |
| Főoldal | GET / | Statikus tartalom |
| Regisztráció | POST /api/register | Új felhasználó létrehozása |
| Bejelentkezés | POST /api/login | Session létrehozása |
| Kijelentkezés | POST /api/logout | Session törlése |
| User státusz | GET /api/user | Aktuális felhasználó |
| Health check | GET /healthz | Alkalmazás állapot |

## Lokális futtatás

```bash
# Python virtuális környezet létrehozása
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Függőségek telepítése
pip install -r requirements.txt

# Locust indítása
locust -f locustfile.py --host=https://csomor-paas-fenykepalbum-3872bd2f225d.herokuapp.com
```

Ezután nyisd meg a böngészőben: http://localhost:8089

## Heroku-n futtatás

Ez a projekt deployolható Herokura, hogy felhőből futtathassuk a terheléspróbát.

```bash
# Heroku app létrehozása
heroku create csomor-fenykepalbum-loadtest

# Deploy
git push heroku main

# Megnyitás
heroku open
```

## Konfiguráció

A Locust Web UI-n beállítható:
- **Number of users**: Szimulált felhasználók száma
- **Spawn rate**: Felhasználók indítási sebessége (/s)
- **Host**: A tesztelendő alkalmazás URL-je

## Ajánlott tesztforgatókönyvek

### 1. Baseline teszt
- Felhasználók: 10
- Spawn rate: 1/s
- Időtartam: 5 perc

### 2. Skálázódási teszt
- Felhasználók: 50-100
- Spawn rate: 5/s
- Időtartam: 10-15 perc

### 3. Stressz teszt
- Felhasználók: 200+
- Spawn rate: 10/s
- Időtartam: 20+ perc
