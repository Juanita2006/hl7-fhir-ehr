from fastapi import FastAPI, HTTPException, Request
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from app.controlador.PatientCrud import GetPatientById, WritePatient, GetPatientByIdentifier
from app.controlador.AppointmentCrud import WriteAppointment
from app.controlador.EncounterCrud import WriteEncounter, WriteEncounterWithResources, WriteCondition, WriteServiceRequest, WriteMedicationRequest

# Crea la aplicación FastAPI
app = FastAPI()

# Configuración CORS actualizada
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hl7-patient-write-juanita-066.onrender.com",
        "https://appointment-write-juanita.onrender.com",
        "https://encounter-write.onrender.com",
        "https://hl7-fhir-ehr-juanita-123.onrender.com",
        "http://localhost:3000"  # Para desarrollo local
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints para Patient
@app.get("/patient", response_model=dict)
async def get_patient_by_identifier(system: str, value: str):
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
    status, patient = GetPatientById(patient_id)
    if status == 'success':
        return patient
    elif status == 'notFound':
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error: {status}")
        
@app.post("/patient", response_model=dict)
async def add_patient(request: Request):
    new_patient_dict = dict(await request.json())
    status, patient_id = WritePatient(new_patient_dict)
    if status == 'success':
        return {"_id": patient_id}
    else:
        raise HTTPException(status_code=500, detail=f"Validation error: {status}")

# Endpoint para Appointment
@app.post("/appointment", response_model=dict)
async def add_appointment(request: Request):
    new_appointment_dict = dict(await request.json())
    status, appointment_id = WriteAppointment(new_appointment_dict)
    
    if status == 'success':
        return {"_id": appointment_id}
    else:
        raise HTTPException(status_code=500, detail=f"Validation error: {status}")

# Endpoints para Encounter y recursos asociados
@app.post("/encounter", response_model=dict)
async def add_encounter(request: Request):
    try:
        data = dict(await request.json())
        
        if "encounter" not in data:
            raise HTTPException(status_code=400, detail="Encounter data is required")
        
        status, encounter_id = WriteEncounterWithResources(data)
        
        if status == 'success':
            return {
                "_id": encounter_id,
                "message": "Encounter and related resources created successfully"
            }
        elif status == 'errorPartialInsert':
            return {
                "_id": encounter_id,
                "warning": "Encounter created but some related resources failed"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating encounter: {status}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/condition", response_model=dict)
async def add_condition(request: Request):
    try:
        condition_data = dict(await request.json())
        status, condition_id = WriteCondition(condition_data)
        
        if status == 'success':
            return {"_id": condition_id}
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating condition: {status}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/servicerequest", response_model=dict)
async def add_service_request(request: Request):
    try:
        service_request_data = dict(await request.json())
        status, service_request_id = WriteServiceRequest(service_request_data)
        
        if status == 'success':
            return {"_id": service_request_id}
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating service request: {status}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/medicationrequest", response_model=dict)
async def add_medication_request(request: Request):
    try:
        medication_request_data = dict(await request.json())
        status, medication_request_id = WriteMedicationRequest(medication_request_data)
        
        if status == 'success':
            return {"_id": medication_request_id}
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating medication request: {status}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
