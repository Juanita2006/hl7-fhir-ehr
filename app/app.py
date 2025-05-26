from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import os
import uvicorn

# Importar todas las funciones CRUD
from app.controlador.PatientCrud import GetPatientById, WritePatient, GetPatientByIdentifier
from app.controlador.AppointmentCrud import WriteAppointment
from app.controlador.EncounterCrud import (
    WriteEncounter,
    WriteCondition,
    WriteServiceRequest,
    WriteMedicationRequest,
    WriteEncounterWithResources
)

# Crear la aplicación FastAPI
app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hl7-patient-write-juanita-066.onrender.com",
        "https://appointment-write-juanita.onrender.com",
        "https://encounter-write.onrender.com",
        "https://hl7-fhir-ehr-juanita-123.onrender.com",
        "*"  # Temporal para desarrollo, quitar en producción
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión a MongoDB
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
patient_db = client["Cluster26"]
patient_collection = patient_db["Patients"]
main_db = client["JYI"]


# --------------------------
# ENDPOINTS PARA PACIENTES
# --------------------------

@app.get("/patient", response_model=dict)
async def get_patient_by_identifier(system: str, value: str):
    """Obtiene un paciente por su identificador"""
    print("Solicitud datos:", system, value)
    status, patient = GetPatientByIdentifier(system, value)
    
    if status == 'success':
        return patient
    elif status == 'notFound':
        raise HTTPException(status_code=204, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error: {status}")

@app.get("/patient/{patient_id}", response_model=dict)
async def get_patient_by_id(patient_id: str):
    """Obtiene un paciente por su ID"""
    status, patient = GetPatientById(patient_id)
    
    if status == 'success':
        return patient
    elif status == 'notFound':
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error: {status}")

@app.post("/patient", response_model=dict)
async def add_patient(request: Request):
    """Crea un nuevo paciente"""
    new_patient_dict = dict(await request.json())
    status, patient_id = WritePatient(new_patient_dict)
    
    if status == 'success':
        return {"_id": patient_id}
    else:
        raise HTTPException(status_code=400, detail=f"Validation error: {status}")

# --------------------------
# ENDPOINTS PARA CITAS
# --------------------------

@app.post("/appointment", response_model=dict)
async def add_appointment(request: Request):
    """Crea una nueva cita médica"""
    new_appointment_dict = dict(await request.json())
    status, appointment_id = WriteAppointment(new_appointment_dict)
    
    if status == 'success':
        return {"_id": appointment_id}
    else:
        raise HTTPException(status_code=400, detail=f"Validation error: {status}")

# --------------------------
# ENDPOINTS PARA ENCUENTROS
# --------------------------

async def handle_resource(request: Request, writer_function, resource_name: str):
    """Función auxiliar para manejar recursos"""
    try:
        data = await request.json()
        print(f">>> {resource_name.upper()} DATA:", data)
        status, inserted_id = writer_function(data)
        
        if status.startswith("success"):
            return {"id": inserted_id}
        return {"error": status}
    except Exception as e:
        print(f"Error en Write{resource_name.capitalize()}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/encounters")
async def post_encounter(request: Request):
    """Crea un nuevo encuentro médico"""
    return await handle_resource(request, WriteEncounter, "encounter")

@app.post("/conditions")
async def post_condition(request: Request):
    """Crea una nueva condición médica"""
    return await handle_resource(request, WriteCondition, "condition")

@app.post("/servicerequests")
async def post_service_request(request: Request):
    """Crea una nueva solicitud de servicio"""
    return await handle_resource(request, WriteServiceRequest, "service_request")

@app.post("/medicationrequests")
async def post_medication_request(request: Request):
    """Crea una nueva solicitud de medicación"""
    return await handle_resource(request, WriteMedicationRequest, "medication_request")

@app.post("/encounter_with_resources")
async def post_encounter_with_resources(request: Request):
    """Crea un encuentro con recursos relacionados"""
    try:
        data = await request.json()
        print(">>> ENCOUNTER WITH RESOURCES:", data)

        status, encounter_id = WriteEncounterWithResources(data)

        if status == "success":
            return {"status": "success", "encounter_id": encounter_id}
        elif status.startswith("partial_success"):
            return {"status": status, "encounter_id": encounter_id}
        else:
            raise HTTPException(status_code=400, detail=status)
    except Exception as e:
        print("Error en /encounter_with_resources:", e)
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------
# INICIO DE LA APLICACIÓN
# --------------------------

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
