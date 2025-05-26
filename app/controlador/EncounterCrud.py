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
        if not encounter_data.get("encounter"):
            return "error: Missing encounter data", None

        # 1. Insertar el Encounter principal
        encounter_status, encounter_id = WriteEncounter(encounter_data["encounter"])
        if encounter_status != "success":
            return encounter_status, None

        # 2. Insertar recursos relacionados
        errors = []
        related_resources = [
            ("condition", WriteCondition),
            ("service_request", WriteServiceRequest),
            ("medication_request", WriteMedicationRequest)
        ]

        for key, writer in related_resources:
            if key in encounter_data:
                resource_block = encounter_data[key]

                # Permitir lista o único objeto
                resource_list = resource_block if isinstance(resource_block, list) else [resource_block]

                for item in resource_list:
                    # Agregar referencia al encounter
                    item["encounter"] = {"reference": f"Encounter/{encounter_id}"}
                    status, _ = writer(item)
                    if status != "success":
                        errors.append(f"{key}")

        if errors:
            return f"partial_success: Failed to save {', '.join(errors)}", encounter_id

        return "success", encounter_id

    except Exception as e:
        print(f"Error en WriteEncounterWithResources: {str(e)}")
        return f"error: {str(e)}", None
