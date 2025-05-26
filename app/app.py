from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import os

# Importar funciones CRUD
from app.controlador.EncounterCrud import (
    WriteEncounter,
    WriteCondition,
    WriteServiceRequest,
    WriteMedicationRequest,
    WriteEncounterWithResources
)

app = FastAPI()

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión a MongoDB (única base de datos: JYI)
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client["JYI"]


# Utilidad común para manejar endpoints simples
async def handle_resource(request: Request, writer_function, resource_name: str):
    try:
        data = await request.json()
        print(f">>> {resource_name.upper()} DATA:", data)
        status, inserted_id = writer_function(data)
        if status.startswith("success"):
            return {"id": inserted_id}
        return {"error": status}
    except Exception as e:
        print(f"Error en Write{resource_name.capitalize()}: {e}")
        return {"error": str(e)}


# Endpoints individuales
@app.get("/patient/{patient_id}", response_model=dict)
async def get_patient_by_id(patient_id: str):
    status,patient = GetPatientById(patient_id)
    if status=='success':
        return patient  # Return patient
    elif status=='notFound':
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error. {status}")

@app.get("/patient", response_model=dict)
async def get_patient_by_identifier(system: str, value: str):
    print("Solicitud datos:",system,value)
    status,patient = GetPatientByIdentifier(system,value)
    if status=='success':
        return patient  # Return patient
    elif status=='notFound':
        raise HTTPException(status_code=204, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error. {status}")


@app.post("/patient", response_model=dict)
async def add_patient(request: Request):
    new_patient_dict = dict(await request.json())
    status,patient_id = WritePatient(new_patient_dict)
    if status=='success':
        return {"_id":patient_id}  # Return patient id
    else:
        raise HTTPException(status_code=500, detail=f"Validating error: {status}")
@app.post("/encounters")
async def post_encounter(request: Request):
    return await handle_resource(request, WriteEncounter, "encounter")


@app.post("/conditions")
async def post_condition(request: Request):
    return await handle_resource(request, WriteCondition, "condition")


@app.post("/servicerequests")
async def post_service_request(request: Request):
    return await handle_resource(request, WriteServiceRequest, "service_request")


@app.post("/medicationrequests")
async def post_medication_request(request: Request):
    return await handle_resource(request, WriteMedicationRequest, "medication_request")


# Endpoint compuesto: Encounter con recursos relacionados
@app.post("/encounter_with_resources")
async def post_encounter_with_resources(request: Request):
    try:
        data = await request.json()
        print(">>> ENCOUNTER WITH RESOURCES:", data)

        status, encounter_id = WriteEncounterWithResources(data)

        if status == "success":
            return {"status": "success", "encounter_id": encounter_id}
        elif status.startswith("partial_success"):
            return {"status": status, "encounter_id": encounter_id}
        else:
            return {"status": status, "encounter_id": encounter_id or None}
    except Exception as e:
        print("Error en /encounter_with_resources:", e)
        return {"error": str(e)}
