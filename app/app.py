from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from fhir.resources.encounter import Encounter
from fhir.resources.condition import Condition
from fhir.resources.servicerequest import ServiceRequest
from fhir.resources.medicationrequest import MedicationRequest
import os

# Importar la función que maneja escritura conjunta
from EncounterCrud import WriteEncounterWithResources

app = FastAPI()

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión a MongoDB
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client["fhir"]

# Colecciones por tipo de recurso
collections = {
    "Encounter": db["encounters"],
    "Condition": db["conditions"],
    "ServiceRequest": db["servicerequests"],
    "MedicationRequest": db["medicationrequests"]
}

# Endpoint para Encounter
@app.post("/encounters")
async def write_encounter(request: Request):
    try:
        body = await request.json()
        print(">>> ENCOUNTER DATA:", body)
        body["resourceType"] = "Encounter"  # Normalizar
        encounter = Encounter(**body)
        result = collections["Encounter"].insert_one(encounter.dict())
        return {"id": str(result.inserted_id)}
    except Exception as e:
        print("Error en WriteEncounter:", e)
        return {"error": str(e)}

# Endpoint para Condition
@app.post("/conditions")
async def write_condition(request: Request):
    try:
        body = await request.json()
        print(">>> CONDITION DATA:", body)
        body["resourceType"] = "Condition"
        condition = Condition(**body)
        result = collections["Condition"].insert_one(condition.dict())
        return {"id": str(result.inserted_id)}
    except Exception as e:
        print("Error en WriteCondition:", e)
        return {"error": str(e)}

# Endpoint para ServiceRequest
@app.post("/servicerequests")
async def write_service_request(request: Request):
    try:
        body = await request.json()
        print(">>> SERVICE REQUEST DATA:", body)
        body["resourceType"] = "ServiceRequest"
        service_request = ServiceRequest(**body)
        result = collections["ServiceRequest"].insert_one(service_request.dict())
        return {"id": str(result.inserted_id)}
    except Exception as e:
        print("Error en WriteServiceRequest:", e)
        return {"error": str(e)}

# Endpoint para MedicationRequest
@app.post("/medicationrequests")
async def write_medication_request(request: Request):
    try:
        body = await request.json()
        print(">>> MEDICATION REQUEST DATA:", body)
        body["resourceType"] = "MedicationRequest"
        medication_request = MedicationRequest(**body)
        result = collections["MedicationRequest"].insert_one(medication_request.dict())
        return {"id": str(result.inserted_id)}
    except Exception as e:
        print("Error en WriteMedicationRequest:", e)
        return {"error": str(e)}

# Nuevo endpoint para escribir Encounter con recursos asociados
@app.post("/encounter_with_resources")
async def encounter_with_resources(request: Request):
    try:
        data = await request.json()
        status, encounter_id = WriteEncounterWithResources(data)

        if status == "success":
            return {"status": "success", "encounter_id": encounter_id}
        elif status.startswith("partial_success"):
            return {"status": status, "encounter_id": encounter_id}
        else:
            return {"status": status}

    except Exception as e:
        print("Error en /encounter_with_resources:", e)
        return {"error": str(e)}
