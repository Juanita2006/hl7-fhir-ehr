from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.patient import Patient
from fhir.resources import FHIRValidationError

collection = connect_to_mongodb("SamplePatientService", "patients")

def GetPatientById(patient_id: str):
    try:
        if not ObjectId.is_valid(patient_id):
            return "invalidId", None
            
        patient = collection.find_one({"_id": ObjectId(patient_id)})
        if not patient:
            return "notFound", None
            
        patient["_id"] = str(patient["_id"])
        return "success", patient
        
    except Exception as e:
        return "serverError", None

def WritePatient(patient_dict: dict):
    try:
        # Validación FHIR
        try:
            pat = Patient.model_validate(patient_dict)
            validated_patient = pat.model_dump()
        except FHIRValidationError as e:
            return "validationError", str(e)
        except Exception as e:
            return "validationError", str(e)
        
        # Inserción en MongoDB
        result = collection.insert_one(validated_patient)
        if not result.inserted_id:
            return "insertError", None
            
        return "success", str(result.inserted_id)
        
    except Exception as e:
        return "serverError", str(e)

def GetPatientByIdentifier(patientSystem: str, patientValue: str):
    try:
        if not patientSystem or not patientValue:
            return "invalidInput", None
            
        patient = collection.find_one({
            "identifier": {
                "$elemMatch": {
                    "system": patientSystem,
                    "value": patientValue
                }
            }
        })
        
        if not patient:
            return "notFound", None
            
        patient["_id"] = str(patient["_id"])
        return "success", patient
        
    except Exception as e:
        return "serverError", str(e)
