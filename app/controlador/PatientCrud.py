from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.patient import Patient
import json

# Conexión a la base de datos y colección "patients"
collection = connect_to_mongodb("SamplePatientService", "patients")

def GetPatientById(patient_id: str):
    try:
        patient = collection.find_one({"_id": ObjectId(patient_id)})
        if patient:
            patient["_id"] = str(patient["_id"])
            return "success", patient
        return "notFound", None
    except Exception as e:
        return "notFound", None

def WritePatient(patient_dict: dict):
    try:
        # Validar con modelo HL7 FHIR
        pat = Patient.model_validate(patient_dict)
    except Exception as e:
        return f"errorValidating: {str(e)}", None

    try:
        # Convertir a estructura JSON serializable
        validated_patient_json = json.loads(pat.model_dump_json())

        # Insertar en MongoDB
        result = collection.insert_one(validated_patient_json)
        if result:
            inserted_id = str(result.inserted_id)
            return "success", inserted_id
        else:
            return "errorInserting", None
    except Exception as e:
        return f"errorInserting: {str(e)}", None

def GetPatientByIdentifier(patientSystem, patientValue):
    try:
        patient = collection.find_one({
            "identifier.system": patientSystem,
            "identifier.value": patientValue
        })
        if patient:
            patient["_id"] = str(patient["_id"])
            return "success", patient
        return "notFound", None
    except Exception as e:
        return f"error encontrado: {str(e)}", None
