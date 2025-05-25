from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.encounter import Encounter
from fhir.resources.condition import Condition
from fhir.resources.servicerequest import ServiceRequest
from fhir.resources.medicationrequest import MedicationRequest

# Conexión a las colecciones de MongoDB
db = connect_to_mongodb("JYI")
encounter_collection = db["encounters"]
condition_collection = db["conditions"]
servicerequest_collection = db["servicerequests"]
medicationrequest_collection = db["medicationrequests"]

def WriteEncounter(encounter_dict: dict):
    """Guarda un recurso Encounter en MongoDB con validación FHIR"""
    try:
        encounter = Encounter.model_validate(encounter_dict)
        validated_encounter = encounter.model_dump()
        result = encounter_collection.insert_one(validated_encounter)
        return "success", str(result.inserted_id)
    except Exception as e:
        print(f"Error validando/insertando Encounter: {str(e)}")
        return f"errorValidating: {str(e)}", None

def WriteCondition(condition_dict: dict):
    """Guarda un recurso Condition en MongoDB con validación FHIR"""
    try:
        condition = Condition.model_validate(condition_dict)
        validated_condition = condition.model_dump()
        result = condition_collection.insert_one(validated_condition)
        return "success", str(result.inserted_id)
    except Exception as e:
        print(f"Error validando/insertando Condition: {str(e)}")
        return "errorValidating", None

def WriteServiceRequest(service_request_dict: dict):
    """Guarda un recurso ServiceRequest en MongoDB con validación FHIR"""
    try:
        service_request = ServiceRequest.model_validate(service_request_dict)
        validated_service_request = service_request.model_dump()
        result = servicerequest_collection.insert_one(validated_service_request)
        return "success", str(result.inserted_id)
    except Exception as e:
        print(f"Error validando/insertando ServiceRequest: {str(e)}")
        return "errorValidating", None

def WriteMedicationRequest(medication_request_dict: dict):
    """Guarda un recurso MedicationRequest en MongoDB con validación FHIR"""
    try:
        medication_request = MedicationRequest.model_validate(medication_request_dict)
        validated_medication_request = medication_request.model_dump()
        result = medicationrequest_collection.insert_one(validated_medication_request)
        return "success", str(result.inserted_id)
    except Exception as e:
        print(f"Error validando/insertando MedicationRequest: {str(e)}")
        return "errorValidating", None

def WriteEncounterWithResources(encounter_data: dict):
    """
    Guarda un Encounter junto con sus recursos asociados en una sola transacción.
    
    Args:
        encounter_data: {
            "encounter": dict,  # Datos del Encounter
            "condition": dict,  # Datos del Condition (opcional)
            "service_request": dict,  # Datos del ServiceRequest (opcional)
            "medication_request": dict  # Datos del MedicationRequest (opcional)
        }
    
    Returns:
        tuple: (status, encounter_id)
    """
    try:
        # 1. Insertar el Encounter primero para obtener su ID
        encounter_status, encounter_id = WriteEncounter(encounter_data["encounter"])
        if encounter_status != "success":
            return "errorEncounter", None
        
        # 2. Insertar recursos asociados si existen
        results = []
        
        if "condition" in encounter_data:
            condition_data = encounter_data["condition"]
            condition_data["encounter"] = {"reference": f"Encounter/{encounter_id}"}
            condition_status, condition_id = WriteCondition(condition_data)
            results.append(condition_status)
        
        if "service_request" in encounter_data:
            service_request_data = encounter_data["service_request"]
            service_request_data["encounter"] = {"reference": f"Encounter/{encounter_id}"}
            service_request_status, service_request_id = WriteServiceRequest(service_request_data)
            results.append(service_request_status)
        
        if "medication_request" in encounter_data:
            medication_request_data = encounter_data["medication_request"]
            medication_request_data["encounter"] = {"reference": f"Encounter/{encounter_id}"}
            medication_request_status, medication_request_id = WriteMedicationRequest(medication_request_data)
            results.append(medication_request_status)
        
        # Verificar que todos los inserts fueron exitosos
        if all(status == "success" for status in results):
            return "success", encounter_id
        else:
            # TODO: Implementar rollback si es necesario
            return "errorPartialInsert", encounter_id
            
    except Exception as e:
        print(f"Error en WriteEncounterWithResources: {str(e)}")
        return "errorSystem", None
