import json
from utils.resource_handler import resource_path

# JSON dosyasının doğru yolu
USERS_PATH = resource_path('data/users.json')

def find_or_create_user(email, name):
    """
    Kullanıcıyı bulur veya yeni kullanıcı oluşturur ve JSON dosyasına kaydeder.
    """
    try:
        with open(USERS_PATH, "r", encoding="utf-8") as file:
            users = json.load(file)
    except FileNotFoundError:
        users = []

    # Mevcut kullanıcıyı kontrol et
    for user in users:
        if user["email"] == email:
            return user

    # Yeni kullanıcı oluştur
    new_user = {"name": name, "email": email, "history": []}
    users.append(new_user)

    # JSON dosyasına kaydet
    with open(USERS_PATH, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4)

    return new_user

def load_users():
    """
    Kullanıcı verilerini yükler.
    """
    try:
        with open(USERS_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Users file not found at {USERS_PATH}.")

def save_users(users):
    """
    Kullanıcı verilerini JSON dosyasına kaydeder.
    """
    try:
        with open(USERS_PATH, "w", encoding="utf-8") as file:
            json.dump(users, file, indent=4)
    except Exception as e:
        raise IOError(f"Failed to save users to {USERS_PATH}: {e}")
