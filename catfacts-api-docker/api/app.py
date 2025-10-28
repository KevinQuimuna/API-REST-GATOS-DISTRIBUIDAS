from fastapi import FastAPI, HTTPException
import requests
import pyodbc
import os
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

load_dotenv()
app = FastAPI(title="API de Hechos de Gatos en Español")

# Conexión a SQL Server - USAR ODBC Driver 18
conn_str = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={os.getenv('DB_SERVER')},{os.getenv('DB_PORT')};"
    f"DATABASE={os.getenv('DB_NAME')};"
    f"UID={os.getenv('DB_USER')};"
    f"PWD={os.getenv('DB_PASSWORD')};"
    f"TrustServerCertificate=yes;"
)

CATFACTS_URL = "https://catfact.ninja/fact"

@app.get("/")
def home():
    return {"mensaje": "🐾 API de Hechos de Gatos en Español funcionando correctamente"}

@app.get("/hecho")
def get_cat_fact():
    """Obtiene un hecho aleatorio de la Cat Facts API y lo traduce al español"""
    try:
        response = requests.get(CATFACTS_URL)
        response.raise_for_status()
        data = response.json()
        fact_english = data["fact"]

        # Traducir al español
        fact_spanish = GoogleTranslator(source="en", target="es").translate(fact_english)

        # Guardar en SQL Server
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO CatFacts (fact_en, fact_es) VALUES (?, ?)", fact_english, fact_spanish)
            conn.commit()

        return {"hecho_en": fact_english, "hecho_es": fact_spanish}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/hechos")
def list_facts():
    """Lista los hechos guardados en la base de datos"""
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, fact_en, fact_es FROM CatFacts ORDER BY id DESC")
            rows = cursor.fetchall()
            
            if not rows:
                return {"mensaje": "No hay hechos guardados aún", "hechos": []}
            
            return {
                "total": len(rows),
                "hechos": [
                    {
                        "id": r[0], 
                        "hecho_en": r[1],
                        "hecho_es": r[2]
                    } for r in rows
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {str(e)}")