from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.patient import Patient

# Asegúrate de que esta colección es la correcta
collection = connect_to_mongodb("SamplePatientService", "patients")

def GetPatientById(patient_id: str):
    try:
        patient = collection.find_one({"_id": ObjectId(patient_id)})
        if patient:
            patient["_id"] = str(patient["_id"])
            return "success", patient
        return "notFound", None
    except Exception as e:
        print(f"Error en GetPatientById: {e}")
        return "error", None

def WritePatient(patient_dict: dict):
    try:
        pat = Patient.model_validate(patient_dict)
        validated_patient_json = pat.model_dump()
        result = collection.insert_one(validated_patient_json)
        if result.inserted_id:
            return "success", str(result.inserted_id)
        else:
            return "errorInserting", None
    except Exception as e:
        print(f"Error en WritePatient: {e}")
        return f"errorValidating: {str(e)}", None

def GetPatientByIdentifier(patientSystem, patientValue):
    try:
        patient = collection.find_one({
            "identifier.system": patientSystem,
            "identifier.value": patientValue
        })
        print("Patient Retornado:", patient)
        if patient:
            patient["_id"] = str(patient["_id"])
            return "success", patient
        return "notFound", None
    except Exception as e:
        print(f"Error en GetPatientByIdentifier: {e}")
        return f"error: {str(e)}", None
