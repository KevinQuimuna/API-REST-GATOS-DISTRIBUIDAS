from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import pyodbc
import os
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from typing import Optional

load_dotenv()
app = FastAPI(title="😺 API CRUD de Hechos de Gatos en Español")

# Conexión a SQL Server
conn_str = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={os.getenv('DB_SERVER')},{os.getenv('DB_PORT')};"
    f"DATABASE={os.getenv('DB_NAME')};"
    f"UID={os.getenv('DB_USER')};"
    f"PWD={os.getenv('DB_PASSWORD')};"
    f"TrustServerCertificate=yes;"
)

CATFACTS_URL = "https://catfact.ninja/fact"

# Modelos Pydantic
class CatFactCreate(BaseModel):
    fact_en: str
    fact_es: Optional[str] = None

class CatFactUpdate(BaseModel):
    fact_en: Optional[str] = None
    fact_es: Optional[str] = None

class CatFactResponse(BaseModel):
    id: int
    fact_en: str
    fact_es: str

# ==================== INTERFAZ WEB ====================

@app.get("/", response_class=HTMLResponse)
def home():
    """Interfaz web principal"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🐱 CRUD Hechos de Gatos</title>
        <style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        min-height: 100vh;
        padding: 20px;
    }
    
    .container {
        max-width: 1200px;
        margin: 0 auto;
        background: white;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    h1 {
        text-align: center;
        color: #3182ce; /* azul */
        margin-bottom: 10px;
        font-size: 2.5em;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 30px;
    }
    
    .actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 15px;
        margin-bottom: 30px;
    }
    
    .btn {
        padding: 15px 25px;
        border: none;
        border-radius: 10px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    
    .btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .btn-primary {
        background: #3182ce; /* azul */
        color: white;
    }
    
    .btn-success {
        background: #48bb78;
        color: white;
    }
    
    .btn-danger {
        background: #f56565;
        color: white;
    }
    
    .btn-warning {
        background: #ed8936;
        color: white;
    }
    
    .form-section {
        background: #f7fafc;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        display: none;
    }
    
    .form-section.active {
        display: block;
    }
    
    .form-group {
        margin-bottom: 15px;
    }
    
    label {
        display: block;
        margin-bottom: 5px;
        color: #2d3748;
        font-weight: 600;
    }
    
    input, textarea {
        width: 100%;
        padding: 12px;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        font-size: 14px;
        transition: border-color 0.3s;
    }
    
    input:focus, textarea:focus {
        outline: none;
        border-color: #3182ce; /* azul */
    }
    
    textarea {
        resize: vertical;
        min-height: 80px;
    }
    
    .facts-list {
        margin-top: 30px;
    }
    
    .fact-card {
        background: #f7fafc;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 5px solid #3182ce; /* azul */
        position: relative;
    }
    
    .fact-card:hover {
        background: #edf2f7;
    }
    
    .fact-id {
        position: absolute;
        top: 10px;
        right: 10px;
        background: #3182ce; /* azul */
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    
    .fact-content {
        margin-bottom: 10px;
    }
    
    .fact-en {
        color: #2d3748;
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    .fact-es {
        color: #4a5568;
    }
    
    .fact-actions {
        display: flex;
        gap: 10px;
        margin-top: 15px;
    }
    
    .btn-small {
        padding: 8px 15px;
        font-size: 14px;
    }
    
    .message {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        display: none;
    }
    
    .message.success {
        background: #c6f6d5;
        color: #22543d;
        border-left: 4px solid #48bb78;
    }
    
    .message.error {
        background: #fed7d7;
        color: #742a2a;
        border-left: 4px solid #f56565;
    }
    
    .message.active {
        display: block;
    }
    
    .loading {
        text-align: center;
        padding: 20px;
        color: #3182ce; /* azul */
        font-weight: bold;
    }
    
    .empty-state {
        text-align: center;
        padding: 40px;
        color: #a0aec0;
    }
    
    .empty-state-icon {
        font-size: 60px;
        margin-bottom: 20px;
    }
</style>

    </head>
    <body>
        <div class="container">
            <h1>🐱 CRUD Hechos de Gatos</h1>
            <p class="subtitle">Gestiona hechos curiosos sobre gatos en inglés y español</p>
            
            <div id="message" class="message"></div>
            
            <div class="actions">
                <button class="btn btn-primary" onclick="loadFacts()">
                    Ver Todos los Hechos
                </button>
                <button class="btn btn-success" onclick="getRandomFact()">
                    Obtener Hecho Aleatorio
                </button>
                <button class="btn btn-warning" onclick="toggleForm('createForm')">
                    Crear Hecho Manual
                </button>
                <button class="btn btn-danger" onclick="confirmDeleteAll()">
                    Eliminar Todos
                </button>
            </div>
            
            <!-- Formulario de Crear -->
            <div id="createForm" class="form-section">
                <h3>Crear Nuevo Hecho</h3>
                <div class="form-group">
                    <label>Hecho en Inglés *</label>
                    <textarea id="create_fact_en" placeholder="Escribe el hecho en inglés..."></textarea>
                </div>
                <div class="form-group">
                    <label>Hecho en Español (opcional - se traduce automáticamente)</label>
                    <textarea id="create_fact_es" placeholder="Traducción al español (opcional)..."></textarea>
                </div>
                <button class="btn btn-success" onclick="createFact()">Guardar Hecho</button>
                <button class="btn btn-danger btn-small" onclick="toggleForm('createForm')">Cancelar</button>
            </div>
            
            <!-- Formulario de Editar -->
            <div id="editForm" class="form-section">
                <h3>Editar Hecho #<span id="edit_id"></span></h3>
                <div class="form-group">
                    <label>Hecho en Inglés</label>
                    <textarea id="edit_fact_en"></textarea>
                </div>
                <div class="form-group">
                    <label>Hecho en Español</label>
                    <textarea id="edit_fact_es"></textarea>
                </div>
                <button class="btn btn-success" onclick="updateFact()">Actualizar Hecho</button>
                <button class="btn btn-danger btn-small" onclick="toggleForm('editForm')">Cancelar</button>
            </div>
            
            <!-- Lista de Hechos -->
            <div class="facts-list">
                <h2>Lista de Hechos</h2>
                <div id="factsList"></div>
            </div>
        </div>
        
        <script>
            let currentEditId = null;
            
            // Cargar hechos al iniciar
            window.onload = function() {
                loadFacts();
            };
            
            // Mostrar mensaje
            function showMessage(text, type = 'success') {
                const msg = document.getElementById('message');
                msg.textContent = text;
                msg.className = `message ${type} active`;
                setTimeout(() => {
                    msg.className = 'message';
                }, 5000);
            }
            
            // Toggle formularios
            function toggleForm(formId) {
                const form = document.getElementById(formId);
                form.classList.toggle('active');
                
                // Limpiar formularios
                if (formId === 'createForm') {
                    document.getElementById('create_fact_en').value = '';
                    document.getElementById('create_fact_es').value = '';
                }
            }
            
            // Cargar todos los hechos
            async function loadFacts() {
                const list = document.getElementById('factsList');
                list.innerHTML = '<div class="loading">Cargando hechos...</div>';
                
                try {
                    const response = await fetch('/api/hechos');
                    const data = await response.json();
                    
                    if (data.hechos.length === 0) {
                        list.innerHTML = `
                            <div class="empty-state">
                                <div class="empty-state-icon">😿</div>
                                <p>No hay hechos guardados aún.</p>
                                <p>Haz clic en "Obtener Hecho Aleatorio" o "Crear Hecho Manual"</p>
                            </div>
                        `;
                        return;
                    }
                    
                    list.innerHTML = data.hechos.map(fact => `
                        <div class="fact-card">
                            <div class="fact-id">ID: ${fact.id}</div>
                            <div class="fact-content">
                                <div class="fact-en">🇬🇧 ${fact.hecho_en}</div>
                                <div class="fact-es">🇪🇸 ${fact.hecho_es}</div>
                            </div>
                            <div class="fact-actions">
                                <button class="btn btn-warning btn-small" onclick="editFact(${fact.id})">
                                    Editar
                                </button>
                                <button class="btn btn-danger btn-small" onclick="deleteFact(${fact.id})">
                                    Eliminar
                                </button>
                            </div>
                        </div>
                    `).join('');
                    
                    showMessage(`Se cargaron ${data.total} hechos`, 'success');
                } catch (error) {
                    list.innerHTML = '<div class="empty-state">Error al cargar los hechos</div>';
                    showMessage('Error al cargar los hechos', 'error');
                }
            }
            
            // Obtener hecho aleatorio de API externa
            async function getRandomFact() {
                try {
                    showMessage('Obteniendo hecho aleatorio...', 'success');
                    const response = await fetch('/api/hecho');
                    const data = await response.json();
                    showMessage(`Hecho guardado: "${data.hecho_es}"`, 'success');
                    loadFacts();
                } catch (error) {
                    showMessage('Error al obtener hecho aleatorio', 'error');
                }
            }
            
            // Crear hecho manual
            async function createFact() {
                const fact_en = document.getElementById('create_fact_en').value.trim();
                const fact_es = document.getElementById('create_fact_es').value.trim();
                
                if (!fact_en) {
                    showMessage('El hecho en inglés es obligatorio', 'error');
                    return;
                }
                
                try {
                    const response = await fetch('/api/hechos', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            fact_en: fact_en,
                            fact_es: fact_es || null
                        })
                    });
                    
                    if (response.ok) {
                        showMessage('Hecho creado exitosamente', 'success');
                        toggleForm('createForm');
                        loadFacts();
                    } else {
                        showMessage('Error al crear el hecho', 'error');
                    }
                } catch (error) {
                    showMessage('Error de conexión', 'error');
                }
            }
            
            // Editar hecho
            async function editFact(id) {
                try {
                    const response = await fetch(`/api/hechos/${id}`);
                    const fact = await response.json();
                    
                    currentEditId = id;
                    document.getElementById('edit_id').textContent = id;
                    document.getElementById('edit_fact_en').value = fact.fact_en;
                    document.getElementById('edit_fact_es').value = fact.fact_es;
                    
                    document.getElementById('editForm').classList.add('active');
                    document.getElementById('editForm').scrollIntoView({ behavior: 'smooth' });
                } catch (error) {
                    showMessage('Error al cargar el hecho', 'error');
                }
            }
            
            // Actualizar hecho
            async function updateFact() {
                const fact_en = document.getElementById('edit_fact_en').value.trim();
                const fact_es = document.getElementById('edit_fact_es').value.trim();
                
                if (!fact_en && !fact_es) {
                    showMessage('Debes proporcionar al menos un campo', 'error');
                    return;
                }
                
                try {
                    const response = await fetch(`/api/hechos/${currentEditId}`, {
                        method: 'PUT',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            fact_en: fact_en || null,
                            fact_es: fact_es || null
                        })
                    });
                    
                    if (response.ok) {
                        showMessage('Hecho actualizado exitosamente', 'success');
                        toggleForm('editForm');
                        loadFacts();
                    } else {
                        showMessage('Error al actualizar el hecho', 'error');
                    }
                } catch (error) {
                    showMessage('Error de conexión', 'error');
                }
            }
            
            // Eliminar hecho
            async function deleteFact(id) {
                if (!confirm(`¿Estás seguro de eliminar el hecho #${id}?`)) return;
                
                try {
                    const response = await fetch(`/api/hechos/${id}`, {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        showMessage(`Hecho #${id} eliminado`, 'success');
                        loadFacts();
                    } else {
                        showMessage(' Error al eliminar el hecho', 'error');
                    }
                } catch (error) {
                    showMessage('Error de conexión', 'error');
                }
            }
            
            // Eliminar todos
            function confirmDeleteAll() {
                if (confirm('¿Estás seguro de eliminar TODOS los hechos? Esta acción no se puede deshacer.')) {
                    deleteAll();
                }
            }
            
            async function deleteAll() {
                try {
                    const response = await fetch('/api/hechos', {
                        method: 'DELETE'
                    });
                    
                    const data = await response.json();
                    showMessage(`${data.mensaje}`, 'success');
                    loadFacts();
                } catch (error) {
                    showMessage('Error al eliminar los hechos', 'error');
                }
            }
        </script>
    </body>
    </html>
    """

# ==================== API ENDPOINTS ====================

@app.post("/api/hechos", response_model=CatFactResponse, status_code=201)
def create_cat_fact(cat_fact: CatFactCreate):
    """Crear un hecho de gato manualmente"""
    try:
        fact_en = cat_fact.fact_en
        fact_es = cat_fact.fact_es
        
        if not fact_es:
            fact_es = GoogleTranslator(source="en", target="es").translate(fact_en)
        
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO CatFacts (fact_en, fact_es) OUTPUT INSERTED.id VALUES (?, ?)",
                fact_en, fact_es
            )
            new_id = cursor.fetchone()[0]
            conn.commit()
        
        return CatFactResponse(id=new_id, fact_en=fact_en, fact_es=fact_es)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el hecho: {str(e)}")

@app.get("/api/hecho")
def get_random_cat_fact():
    """Obtiene un hecho aleatorio de la Cat Facts API externa"""
    try:
        response = requests.get(CATFACTS_URL)
        response.raise_for_status()
        data = response.json()
        fact_english = data["fact"]

        fact_spanish = GoogleTranslator(source="en", target="es").translate(fact_english)

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO CatFacts (fact_en, fact_es) OUTPUT INSERTED.id VALUES (?, ?)",
                fact_english, fact_spanish
            )
            new_id = cursor.fetchone()[0]
            conn.commit()

        return {
            "id": new_id,
            "hecho_en": fact_english,
            "hecho_es": fact_spanish
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/hechos")
def list_all_facts(limit: int = 100, offset: int = 0):
    """Lista todos los hechos guardados"""
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM CatFacts")
            total = cursor.fetchone()[0]
            
            cursor.execute(
                """
                SELECT id, fact_en, fact_es 
                FROM CatFacts 
                ORDER BY id DESC 
                OFFSET ? ROWS 
                FETCH NEXT ? ROWS ONLY
                """,
                offset, limit
            )
            rows = cursor.fetchall()
            
            return {
                "total": total,
                "limit": limit,
                "offset": offset,
                "hechos": [
                    {
                        "id": r[0],
                        "hecho_en": r[1],
                        "hecho_es": r[2]
                    } for r in rows
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/hechos/{fact_id}", response_model=CatFactResponse)
def get_fact_by_id(fact_id: int):
    """Obtener un hecho específico por ID"""
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, fact_en, fact_es FROM CatFacts WHERE id = ?",
                fact_id
            )
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"Hecho con ID {fact_id} no encontrado")
            
            return CatFactResponse(id=row[0], fact_en=row[1], fact_es=row[2])
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.put("/api/hechos/{fact_id}", response_model=CatFactResponse)
def update_cat_fact(fact_id: int, cat_fact: CatFactUpdate):
    """Actualizar un hecho existente"""
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, fact_en, fact_es FROM CatFacts WHERE id = ?", fact_id)
            existing = cursor.fetchone()
            
            if not existing:
                raise HTTPException(status_code=404, detail=f"Hecho con ID {fact_id} no encontrado")
            
            new_fact_en = cat_fact.fact_en if cat_fact.fact_en else existing[1]
            new_fact_es = cat_fact.fact_es if cat_fact.fact_es else existing[2]
            
            if cat_fact.fact_en and not cat_fact.fact_es:
                new_fact_es = GoogleTranslator(source="en", target="es").translate(new_fact_en)
            
            cursor.execute(
                "UPDATE CatFacts SET fact_en = ?, fact_es = ? WHERE id = ?",
                new_fact_en, new_fact_es, fact_id
            )
            conn.commit()
            
            return CatFactResponse(id=fact_id, fact_en=new_fact_en, fact_es=new_fact_es)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.delete("/api/hechos/{fact_id}")
def delete_cat_fact(fact_id: int):
    """Eliminar un hecho por ID"""
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM CatFacts WHERE id = ?", fact_id)
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Hecho con ID {fact_id} no encontrado")
            
            cursor.execute("DELETE FROM CatFacts WHERE id = ?", fact_id)
            conn.commit()
            
            return {
                "mensaje": f"Hecho con ID {fact_id} eliminado exitosamente",
                "id": fact_id
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.delete("/api/hechos")
def delete_all_facts():
    """Eliminar todos los hechos"""
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM CatFacts")
            count = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM CatFacts")
            conn.commit()
            
            return {
                "mensaje": f"Se eliminaron {count} hechos exitosamente",
                "total_eliminados": count
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")