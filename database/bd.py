import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # charge .env

def get_connection():
    return psycopg2.connect(os.getenv("https://kdydhtxtfpknhehjxwmy.supabase.co"))

def fetch(query, params=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    result = cur.fetchall()
    conn.close()
    return result

def execute(query, params=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()
