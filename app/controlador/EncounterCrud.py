from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.encounter import Encounter
from fhir.resources.condition import Condition
from fhir.resources.servicerequest import ServiceRequest
from fhir.resources.medicationrequest import MedicationRequest
from pymongo import MongoClient

def connect_to_mongodb():
    """Obtiene las colecciones de MongoDB con manejo de errores"""
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["JYI"]
        return {
            "encounters": db["encounters"],
            "conditions": db["conditions"],
            "servicerequests": db["servicerequests"],
            "medicationrequests": db["medicationrequests"]
        }
    except Exception as e:
        print(f"Error conectando a MongoDB: {str(e)}")
        raise

collections = get_collections()

def WriteEncounter(encounter_dict: dict):
    """Guarda un recurso Encounter validado"""
    try:
        encounter = Encounter.model_validate(encounter_dict)
        result = collections["encounters"].insert_one(encounter.model_dump())
        return "success", str(result.inserted_id)
    except Exception as e:
        print(f"Error en WriteEncounter: {str(e)}")
        return f"error: {str(e)}", None

def WriteCondition(condition_dict: dict):
    """Guarda un recurso Condition validado"""
    try:
        condition = Condition.model_validate(condition_dict)
        result = collections["conditions"].insert_one(condition.model_dump())
        return "success", str(result.inserted_id)
    except Exception as e:
        print(f"Error en WriteCondition: {str(e)}")
        return f"error: {str(e)}", None

def WriteServiceRequest(service_request_dict: dict):
    """Guarda un recurso ServiceRequest validado"""
    try:
        service_request = ServiceRequest.model_validate(service_request_dict)
        result = collections["servicerequests"].insert_one(service_request.model_dump())
        return "success", str(result.inserted_id)
    except Exception as e:
        print(f"Error en WriteServiceRequest: {str(e)}")
        return f"error: {str(e)}", None

def WriteMedicationRequest(medication_request_dict: dict):
    """Guarda un recurso MedicationRequest validado"""
    try:
        medication_request = MedicationRequest.model_validate(medication_request_dict)
        result = collections["medicationrequests"].insert_one(medication_request.model_dump())
        return "success", str(result.inserted_id)
    except Exception as e:
        print(f"Error en WriteMedicationRequest: {str(e)}")
        return f"error: {str(e)}", None

def WriteEncounterWithResources(encounter_data: dict):
    """
    Guarda un Encounter con sus recursos asociados de forma atómica
    Args:
        encounter_data: {
            "encounter": dict,
            "condition": dict (opcional),
            "service_request": dict (opcional),
            "medication_request": dict (opcional)
        }
    Returns:
        tuple: (status, encounter_id)
    """
    try:
        # Validación inicial
        if not encounter_data.get("encounter"):
            return "error: Missing encounter data", None

        # Insertar Encounter primero
        encounter_status, encounter_id = WriteEncounter(encounter_data["encounter"])
        if encounter_status != "success":
            return encounter_status, None

        # Procesar recursos asociados
        resources = [
            ("condition", WriteCondition),
            ("service_request", WriteServiceRequest),
            ("medication_request", WriteMedicationRequest)
        ]

        errors = []
        for resource_name, writer in resources:
            if resource_name in encounter_data:
                data = encounter_data[resource_name]
                data["encounter"] = {"reference": f"Encounter/{encounter_id}"}
                status, _ = writer(data)
                if status != "success":
                    errors.append(resource_name)

        if errors:
            return f"partial_success: Failed to save {', '.join(errors)}", encounter_id
        return "success", encounter_id

    except Exception as e:
        print(f"Error en WriteEncounterWithResources: {str(e)}")
        return f"error: {str(e)}", None
