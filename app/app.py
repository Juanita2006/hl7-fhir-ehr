from fastapi import FastAPI, HTTPException, Request
import uvicorn
from app.controlador.PatientCrud import GetPatientById,WritePatient,GetPatientByIdentifier
from app.controlador.AppointmentCrud import WriteAppointment 
from app.controlador.EncounterCrud import WriteEncounter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hl7-patient-write-juanita-066.onrender.com","https://appointment-write-juanita.onrender.com","https://encounter-write.onrender.com"],  # Permitir solo este dominio
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)
@app.get("/patient", response_model=dict)
async def get_patient_by_identifier(system: str, value: str):
    print("solicitud datos:",system,value)
    status,patient = GetPatientByIdentifier(system,value)
    if status=='success':
        return patient 
    elif status=='notFound':
        raise HTTPException(status_code=204, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error, (status)")
        
@app.get("/patient/{patient_id}", response_model=dict)
async def get_patient_by_id(patient_id: str):
    status,patient = GetPatientById(patient_id)
    if status=='success':
        return patient  # Return patient
    elif status=='notFound':
        raise HTTPException(status_code=404, detail="Patient not found")
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
@app.post("/appointment", response_model=dict)
async def add_appointment(request: Request):
    new_appointment_dict = dict(await request.json())
    status, appointment_id = WriteAppointment(new_appointment_dict)
    
    if status == 'success':
        return {"_id": appointment_id}  # Retornar ID de la cita
    else:
        raise HTTPException(status_code=500, detail=f"Validating error: {status}")

from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.post("/encounter", response_model=dict)
async def add_encounter(request: Request):
    new_encounter_dict = dict(await request.json())
    status, encounter_id = WriteEncounter(new_encounter_dict)

    if status == 'success':
        return {"_id": encounter_id}  # Retornar ID del encuentro
    else:
        raise HTTPException(status_code=500, detail=f"Validating error: {status}")

from fastapi import HTTPException, Request 
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

