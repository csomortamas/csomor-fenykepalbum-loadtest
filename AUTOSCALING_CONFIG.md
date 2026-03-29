# Automatikus Skálázódás Konfiguráció - Heroku

## Tartalomjegyzék

1. [Bevezetés](#bevezetés)
2. [Heroku Autoscaling lehetőségek](#heroku-autoscaling-lehetőségek)
3. [Konfiguráció lépései](#konfiguráció-lépései)
4. [Erőforrás-korlátozás](#erőforrás-korlátozás)
5. [Monitoring és metrikák](#monitoring-és-metrikák)
6. [Terheléspróba futtatása](#terheléspróba-futtatása)

---

## Bevezetés

Ez a dokumentáció a **csomor-paas-fenykepalbum** alkalmazás automatikus skálázódásának konfigurálását írja le Heroku platformon.

### Cél
- Automatikus felskálázódás nagy terhelésnél
- Automatikus visszaskálázódás a terhelés csökkenésekor
- Költséghatékony erőforrás-felhasználás

---

## Heroku Autoscaling lehetőségek

### 1. Heroku Autoscaling (Performance/Private dynos)

A Heroku beépített autoscaling funkciója **csak Performance és Private dyno típusokhoz** érhető el.

**Konfiguráció a Dashboard-on:**
1. Navigálj az alkalmazáshoz: https://dashboard.heroku.com/apps/csomor-paas-fenykepalbum
2. **Resources** tab
3. **Enable Autoscaling** a web dyno mellett
4. Állítsd be:
   - Min dynos: 1
   - Max dynos: 5
   - Target Response Time: 200ms

### 2. Add-on alapú autoscaling (Eco/Basic dynos)

Eco és Basic dynokhoz külső megoldások használhatók:

#### HireFire (Ajánlott)
```bash
# Add-on hozzáadása
heroku addons:create hirefire -a csomor-paas-fenykepalbum

# Dashboard megnyitása
heroku addons:open hirefire -a csomor-paas-fenykepalbum
```

**HireFire konfiguráció:**
- Manager: web
- Min dynos: 1
- Max dynos: 5
- Strategy: Queue/Job time vagy Response time
- Scale up threshold: Response time > 500ms
- Scale down threshold: Response time < 100ms

#### Rails Autoscale
```bash
heroku addons:create rails-autoscale -a csomor-paas-fenykepalbum
```

### 3. Heroku Scheduler + Script (DIY megoldás)

Egyszerű időalapú skálázás:

```bash
# Scheduler add-on hozzáadása
heroku addons:create scheduler:standard -a csomor-paas-fenykepalbum

# Job hozzáadása (Dashboard-on)
# Csúcsidőben (reggel 8-tól): heroku ps:scale web=3 -a csomor-paas-fenykepalbum
# Éjszaka (este 10-kor): heroku ps:scale web=1 -a csomor-paas-fenykepalbum
```

---

## Konfiguráció lépései

### 1. lépés: Dyno típus kiválasztása

**Labor célokra (költséghatékony teszteléshez):**
```bash
# Eco dyno - legolcsóbb, de korlátozott
heroku ps:type eco -a csomor-paas-fenykepalbum

# VAGY Basic dyno - állandóan fut
heroku ps:type basic -a csomor-paas-fenykepalbum
```

**Production környezethez:**
```bash
# Standard-1X dyno
heroku ps:type standard-1x -a csomor-paas-fenykepalbum

# Performance-M (autoscaling támogatással)
heroku ps:type performance-m -a csomor-paas-fenykepalbum
```

### 2. lépés: Manuális skálázás tesztelése

```bash
# Jelenlegi állapot ellenőrzése
heroku ps -a csomor-paas-fenykepalbum

# 3 dyno-ra skálázás
heroku ps:scale web=3 -a csomor-paas-fenykepalbum

# Vissza 1 dyno-ra
heroku ps:scale web=1 -a csomor-paas-fenykepalbum
```

### 3. lépés: Autoscaling aktiválása

**HireFire használatával (ajánlott labor környezetben):**

1. Add-on telepítése:
```bash
heroku addons:create hirefire:basic -a csomor-paas-fenykepalbum
```

2. HireFire Dashboard megnyitása:
```bash
heroku addons:open hirefire -a csomor-paas-fenykepalbum
```

3. Manager létrehozása:
   - **Process**: web
   - **Min Dynos**: 1
   - **Max Dynos**: 5 (vagy a kívánt maximum)
   - **Strategy**: Heroku Response Time
   - **Upscale threshold**: 500ms
   - **Downscale threshold**: 100ms
   - **Cooldown**: 3 minutes

---

## Erőforrás-korlátozás

### Memory korlátozás (kis terheléshez is skálázás)

A Node.js memóriahasználata korlátozható:

**Procfile módosítása:**
```
release: node init-db.js
web: node --max-old-space-size=128 server.js
```

Ez 128MB-ra korlátozza a heap méretet, ami hamarabb kiváltja a skálázást.

### WEB_CONCURRENCY

Express alkalmazásoknál használható a cluster mód:

```javascript
// Procfile módosítás cluster módhoz (opcionális)
// web: npm start
```

```bash
# WEB_CONCURRENCY beállítása
heroku config:set WEB_CONCURRENCY=1 -a csomor-paas-fenykepalbum
```

---

## Monitoring és metrikák

### Heroku Metrics Dashboard

```bash
# Dashboard megnyitása
heroku addons:open metrics -a csomor-paas-fenykepalbum
```

**Figyelt metrikák:**
- Response Time (p95, p99)
- Throughput (req/min)
- Memory Usage
- Dyno Load
- Error Rate

### Heroku Logs

```bash
# Valós idejű log követés
heroku logs --tail -a csomor-paas-fenykepalbum

# Router logok (response time látható)
heroku logs --tail --source=heroku --dyno=router -a csomor-paas-fenykepalbum
```

### Dyno állapot figyelése

```bash
# Futó dynok listázása
heroku ps -a csomor-paas-fenykepalbum

# Dyno információk
heroku ps:type -a csomor-paas-fenykepalbum
```

---

## Terheléspróba futtatása

### 1. Locust indítása (felhőből)

```bash
# Locust app megnyitása
heroku open -a csomor-fenykepalbum-loadtest
```

### 2. Teszt paraméterek

**Skálázódás demonstrálásához:**
- Host: `https://csomor-paas-fenykepalbum-3872bd2f225d.herokuapp.com`
- Number of users: 100
- Spawn rate: 10/s
- Run time: 10-15 perc

### 3. Megfigyelés

Párhuzamosan figyeld:
- Heroku Dashboard (Metrics)
- `heroku ps -a csomor-paas-fenykepalbum` (dyno szám változása)
- HireFire Dashboard (skálázási események)

### 4. Eredmények dokumentálása

A terheléspróba közben készíts:
- Screenshot a Locust statisztikákról
- Screenshot a Heroku Metrics-ről
- Screenshot a dyno skálázási eseményekről
- Log részletek a skálázódásról

---

## Összefoglaló parancsok

```bash
# App státusz
heroku ps -a csomor-paas-fenykepalbum

# Manuális skálázás
heroku ps:scale web=3 -a csomor-paas-fenykepalbum

# Config vars
heroku config -a csomor-paas-fenykepalbum

# Add-onok
heroku addons -a csomor-paas-fenykepalbum

# Logok
heroku logs --tail -a csomor-paas-fenykepalbum

# Dyno típus váltás
heroku ps:type standard-1x -a csomor-paas-fenykepalbum
```

---

## Költségbecslés

| Dyno típus | Ár/óra | Ár/hó | Autoscaling |
|------------|--------|-------|-------------|
| Eco | $0.01 | $5 | HireFire |
| Basic | $0.01 | $7 | HireFire |
| Standard-1X | $0.035 | $25 | HireFire |
| Standard-2X | $0.069 | $50 | HireFire |
| Performance-M | $0.347 | $250 | Beépített |

**Megjegyzés:** A labor célokra a Basic vagy Standard-1X dyno + HireFire kombináció ajánlott.
