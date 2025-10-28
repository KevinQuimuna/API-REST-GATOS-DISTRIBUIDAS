# API de Hechos de Gatos en Español

API REST contenerizada con FastAPI que obtiene datos de gatos desde una API externa, los traduce al español usando Google Translator y los almacena en SQL Server.

# Arquitectura
```
Cliente (Browaer)----Api fastapi (cat facts)-----sql server dcoker
```

## Requisitos Previos

- Docker Desktop instalado y corriendo
- Docker Compose
- Puertos 8000 y 1433 disponibles

### 1. Clonar/Descargar el proyecto
```bash
cd catfacts-api-docker
```

### 2. Estructura de archivos
```
catfacts-api-docker/
├── docker-compose.yml
├── README.md
├── api/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
└── db/
    └── init.sql
```

### 3. Levantar los contenedores
```bash
docker-compose up --build
```

Espera a ver el mensaje:
```
api_container  | INFO: Uvicorn running on http://0.0.0.0:8000
```

## Uso de la API

### Endpoints disponibles

| Método | Endpoint   | Descripción                                    |
|--------|-----------|------------------------------------------------|
| GET    | `/`       | Status de la API                               |
| GET    | `/hecho`  | Obtiene un hecho aleatorio traducido al español |
| GET    | `/hechos` | Lista todos los hechos guardados               |

### Ejemplos de uso

**Desde PowerShell/CMD:**
```powershell
curl http://localhost:8000/
curl http://localhost:8000/hecho
curl http://localhost:8000/hechos
```

**Desde el navegador:**
- Documentación interactiva: http://localhost:8000/docs
- Endpoint principal: http://localhost:8000/

### Respuestas de ejemplo

**GET /hecho**
```json
{
  "hecho_en": "Cats have 32 muscles in each ear.",
  "hecho_es": "Los gatos tienen 32 músculos en cada oreja."
}
```

**GET /hechos**
```json
{
  "total": 2,
  "hechos": [
    {
      "id": 2,
      "hecho_en": "Cats sleep 70% of their lives.",
      "hecho_es": "Los gatos duermen el 70% de sus vidas."
    },
    {
      "id": 1,
      "hecho_en": "A group of cats is called a clowder.",
      "hecho_es": "Un grupo de gatos se llama clowder."
    }
  ]
}
```

## Base de Datos

### Acceder a SQL Server directamente
```bash
docker exec -it sqlserver_container /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "StrongPassword123!" -C \
  -Q "SELECT * FROM CatFactsDB.dbo.CatFacts"
```

### Estructura de la tabla
```sql
CREATE TABLE CatFacts (
    id INT IDENTITY(1,1) PRIMARY KEY,
    fact_en NVARCHAR(255),
    fact_es NVARCHAR(255)
);
```

## Detener la aplicación
```bash
# Detener sin eliminar datos
docker-compose down

# Detener y eliminar volúmenes (borra datos)
docker-compose down -v
```

## Tecnologías utilizadas

- **FastAPI** - Framework web moderno para Python
- **SQL Server 2022 Express** - Base de datos relacional
- **Docker & Docker Compose** - Contenerización y orquestación
- **pyodbc** - Conector Python-SQL Server
- **deep-translator** - Traducción automática
- **uvicorn** - Servidor ASGI

## Variables de entorno (api/.env)
```properties
DB_SERVER=sqlserver
DB_NAME=CatFactsDB
DB_USER=sa
DB_PASSWORD=StrongPassword123!
DB_PORT=1433
```


### Error: Puerto 8000 ya está en uso
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux
lsof -ti:8000 | xargs kill -9
```

### Error: No se puede conectar a SQL Server
```bash
docker logs sqlserver_container
docker logs api_container
```

### Reiniciar desde cero
```bash
docker-compose down -v
docker-compose up --build
```

## Autor

Kevin Quimuña - Aplicaciones Distribuidas 

# 2. Levantar
docker-compose up --build

# 3. Probar
# Abrir http://localhost:8000/docs en el navegador
