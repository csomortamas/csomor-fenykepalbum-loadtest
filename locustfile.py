"""
Fényképalbum alkalmazás terheléspróba - Locust

Ez a fájl tartalmazza a terheléspróba forgatókönyvét, amely lefedi
a fényképalbum összes fő funkcióját:
- Főoldal betöltése
- Fotók listázása (lapozással)
- Egyedi fotó lekérése
- Felhasználó regisztráció
- Bejelentkezés
- Kijelentkezés
- Aktuális felhasználó lekérdezése
"""

from locust import HttpUser, task, between, events
import random
import string
import logging

# Logging beállítása
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def random_string(length=8):
    """Véletlenszerű string generálása"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


class PhotoAlbumUser(HttpUser):
    """
    Fényképalbum felhasználó szimulációja.
    Minden virtuális felhasználó véletlenszerűen hajtja végre a különböző műveleteket.
    """

    # Kérések közötti várakozási idő (1-3 másodperc)
    wait_time = between(1, 3)

    # Felhasználói adatok tárolása
    username = None
    password = None
    is_logged_in = False
    known_photo_ids = []

    def on_start(self):
        """Inicializálás: opcionálisan regisztrál és bejelentkezik"""
        # 30% eséllyel regisztrál új felhasználót
        if random.random() < 0.3:
            self.register_user()

    def register_user(self):
        """Új felhasználó regisztrálása"""
        self.username = f"loadtest_{random_string(10)}"
        self.password = random_string(12)

        response = self.client.post("/api/register", json={
            "username": self.username,
            "password": self.password
        }, name="/api/register")

        if response.status_code == 200:
            self.is_logged_in = True
            logger.info(f"Registered user: {self.username}")
        else:
            logger.warning(f"Registration failed: {response.status_code}")

    @task(10)
    def get_photos_list(self):
        """Fotók listázása - ez a leggyakoribb művelet"""
        page = random.randint(1, 5)
        sort = random.choice(['name', 'date'])

        response = self.client.get(
            f"/api/photos?page={page}&limit=10&sort={sort}",
            name="/api/photos"
        )

        if response.status_code == 200:
            try:
                data = response.json()
                # Tároljuk a fotó ID-kat későbbi lekérdezésekhez
                for item in data.get('items', []):
                    if item.get('id') and item['id'] not in self.known_photo_ids:
                        self.known_photo_ids.append(item['id'])
            except:
                pass

    @task(5)
    def get_single_photo(self):
        """Egyedi fotó lekérése"""
        if self.known_photo_ids:
            photo_id = random.choice(self.known_photo_ids)
            self.client.get(f"/api/photos/{photo_id}", name="/api/photos/:id")
        else:
            # Ha nincs ismert fotó, próbáljunk meg egyet lekérni
            self.client.get("/api/photos/1", name="/api/photos/:id")

    @task(8)
    def load_homepage(self):
        """Főoldal betöltése (statikus tartalom)"""
        self.client.get("/", name="/ (homepage)")

    @task(3)
    def check_user_status(self):
        """Felhasználói státusz ellenőrzése"""
        self.client.get("/api/user", name="/api/user")

    @task(2)
    def login_logout_cycle(self):
        """Bejelentkezés-kijelentkezés ciklus"""
        if not self.username:
            # Ha nincs felhasználónk, regisztráljunk
            self.register_user()

        if self.username and not self.is_logged_in:
            # Bejelentkezés
            response = self.client.post("/api/login", json={
                "username": self.username,
                "password": self.password
            }, name="/api/login")

            if response.status_code == 200:
                self.is_logged_in = True

        elif self.is_logged_in:
            # Kijelentkezés
            response = self.client.post("/api/logout", name="/api/logout")
            if response.status_code == 200:
                self.is_logged_in = False

    @task(1)
    def health_check(self):
        """Health check endpoint tesztelése"""
        self.client.get("/healthz", name="/healthz")


class HeavyLoadUser(HttpUser):
    """
    Intenzív terhelést generáló felhasználó.
    Minimális várakozással, gyors egymás utáni kéréseket küld.
    """

    wait_time = between(0.1, 0.5)

    @task(10)
    def rapid_photo_list(self):
        """Gyors fotólista lekérések"""
        self.client.get("/api/photos?page=1&limit=10", name="/api/photos (heavy)")

    @task(5)
    def rapid_homepage(self):
        """Gyors főoldal lekérések"""
        self.client.get("/", name="/ (heavy)")


# Event handler a teszt indításakor
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    logger.info("=" * 50)
    logger.info("Fényképalbum terheléspróba indítása")
    logger.info("=" * 50)


# Event handler a teszt végén
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    logger.info("=" * 50)
    logger.info("Fényképalbum terheléspróba befejezve")
    logger.info("=" * 50)
