import sys, os
# On ajoute le dossier racine du projet (parent de /database/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import hashlib
import jwt
import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db_sql import execute_query
from engine.game import run_game
app = FastAPI(title="Roguelike API", version="1.1")


# --------------------------
# CONFIGURATION JWT
# --------------------------
SECRET_KEY = "REMPLACE_CECI_PAR_UNE_CLE_SECRETE_FORTE"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 12
security = HTTPBearer()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRE_HOURS),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")

# --------------------------
# ROUTES UTILISATEURS
# --------------------------

@app.post("/register")
def register_user(username: str, email: str, password: str):
    check = execute_query("SELECT id FROM utilisateurs WHERE username = %s;", (username,), fetch="one")
    if check:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris.")

    hashed = hash_password(password)
    execute_query(
        "INSERT INTO utilisateurs (username, email, mdp) VALUES (%s, %s, %s);",
        (username, email, hashed)
    )
    user = execute_query("SELECT id, username, email FROM utilisateurs WHERE username = %s;", (username,), fetch="one")
    return {"message": "✅ Utilisateur créé avec succès.", "user": {"id": user[0], "username": user[1], "email": user[2]}}

@app.post("/login")
def login_user(username: str, password: str):
    hashed = hash_password(password)
    user = execute_query(
        "SELECT id, username FROM utilisateurs WHERE username = %s AND mdp = %s;",
        (username, hashed),
        fetch="one"
    )
    if not user:
        raise HTTPException(status_code=401, detail="Identifiants invalides.")
    
    token = create_token(user[0])
    return {"message": f"Bienvenue {user[1]} !", "token": token, "user_id": user[0]}

@app.post("/game/start")
def start_game(user_id: int = Depends(verify_token)):
    check = execute_query("SELECT id, username FROM utilisateurs WHERE id = %s;", (user_id,), fetch="one")
    if not check:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    
    print(f"🎮 Lancement du jeu pour {check[1]} (ID {user_id}) ...")
    run_game()
    return {"message": f"Partie lancée pour {check[1]} !"}

@app.get("/")
def root():
    return {"message": "Bienvenue sur l’API Roguelike 🚀"}
