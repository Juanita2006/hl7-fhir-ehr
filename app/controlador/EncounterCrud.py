from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.encounter import Encounter

# Conexión a la colección de encounters
collection = connect_to_mongodb("Encounter", "Consulta")

def WriteEncounter(encounter_dict: dict):
    try:
        # Validar que cumple el formato FHIR
        encounter = Encounter.model_validate(encounter_dict)
    except Exception as e:
        print("Error validando encounter:", str(e))
        return f"errorValidating: {str(e)}", None

    # Convertir a diccionario limpio y guardar en MongoDB
    validated_encounter_json = encounter.model_dump()

    # Insertar encounter validado en MongoDB
    try:
        result = collection.insert_one(validated_encounter_json)
        if result.inserted_id:
            inserted_id = str(result.inserted_id)
            return "success", inserted_id
        else:
            return "errorInserting", None
    except Exception as e:
        print(f"Error insertando encounter: {str(e)}")
        return "errorInserting", None

