from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.encounter import Encounter
from fhir.resources.condition import Condition
from fhir.resources.servicerequest import ServiceRequest
from fhir.resources.medicationrequest import MedicationRequest

# Conexión a las colecciones en la base de datos JYI
encounters_col = connect_to_mongodb("JYI", "encounters")
conditions_col = connect_to_mongodb("JYI", "conditions")
servicerequests_col = connect_to_mongodb("JYI", "servicerequests")
medicationrequests_col = connect_to_mongodb("JYI", "medicationrequests")


def fix_resource_type(data: dict, correct_type: str):
    """Asegura que el campo resourceType tenga el valor correcto."""
    if "resourceType" in data and data["resourceType"].lower() != correct_type.lower():
        data["resourceType"] = correct_type
    elif "resourceType" not in data:
        data["resourceType"] = correct_type
    return data


def WriteEncounter(encounter_dict: dict):
    try:
        fix_resource_type(encounter_dict, "Encounter")
        encounter = Encounter.model_validate(encounter_dict)
        result = encounters_col.insert_one(encounter.model_dump())
        return "success", str(result.inserted_id)
    except Exception as e:
        print(f"Error en WriteEncounter: {str(e)}")
        return f"error: {str(e)}", None


def WriteCondition(condition_dict: dict):
    try:
        fix_resource_type(condition_dict, "Condition")
        condition = Condition.model_validate(condition_dict)
        result = conditions_col.insert_one(condition.model_dump())
        return "success", str(result.inserted_id)
    except Exception as e:
        print(f"Error en WriteCondition: {str(e)}")
        return f"error: {str(e)}", None


def WriteServiceRequest(service_request_dict: dict):
    try:
        fix_resource_type(service_request_dict, "ServiceRequest")
        service_request = ServiceRequest.model_validate(service_request_dict)
        result = servicerequests_col.insert_one(service_request.model_dump())
        return "success", str(result.inserted_id)
    except Exception as e:
        print(f"Error en WriteServiceRequest: {str(e)}")
        return f"error: {str(e)}", None


def WriteMedicationRequest(medication_request_dict: dict):
    try:
        fix_resource_type(medication_request_dict, "MedicationRequest")
        medication_request = MedicationRequest.model_validate(medication_request_dict)
        result = medicationrequests_col.insert_one(medication_request.model_dump())
        return "success", str(result.inserted_id)
    except Exception as e:
        print(f"Error en WriteMedicationRequest: {str(e)}")
        return f"error: {str(e)}", None


def WriteEncounterWithResources(encounter_data: dict):
    try:
        # 1. Extraer y validar partes
        encounter = encounter_data.get("encounter")
        condition_data = encounter_data.get("condition")
        service_request_data = encounter_data.get("service_request")
        medication_request_data = encounter_data.get("medication_request")

        if not encounter:
            return "error: Missing encounter data", None

        # 2. Insertar el Encounter principal
        status_e, encounter_id = WriteEncounter(encounter)
        if status_e != "success":
            return status_e, None

        # 3. Preparar Encounter reference
        encounter_ref = {"reference": f"Encounter/{encounter_id}"}

        # 4. Insertar Condition(es)
        errors = []

        if condition_data:
            condition_list = condition_data if isinstance(condition_data, list) else [condition_data]
            for condition in condition_list:
                condition["encounter"] = encounter_ref
                status, _ = WriteCondition(condition)
                if status != "success":
                    errors.append("condition")

        # 5. Insertar ServiceRequest(s)
        if service_request_data:
            sr_list = service_request_data if isinstance(service_request_data, list) else [service_request_data]
            for sr in sr_list:
                sr["encounter"] = encounter_ref
                status, _ = WriteServiceRequest(sr)
                if status != "success":
                    errors.append("service_request")

        # 6. Insertar MedicationRequest(s)
        if medication_request_data:
            mr_list = medication_request_data if isinstance(medication_request_data, list) else [medication_request_data]
            for mr in mr_list:
                mr["encounter"] = encounter_ref
                status, _ = WriteMedicationRequest(mr)
                if status != "success":
                    errors.append("medication_request")

        if errors:
            return f"partial_success: Failed to save {', '.join(set(errors))}", encounter_id

        return "success", encounter_id

    except Exception as e:
        print(f"Error en WriteEncounterWithResources: {str(e)}")
        return f"error: {str(e)}", None

