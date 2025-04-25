from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.encounter import Encounter

# Conexión a la base de datos y colección para encuentros clínicos
collection = connect_to_mongodb("JYI", "encounters")  # Cambia el nombre de la colección si lo necesitas

def WriteEncounter(encounter_dict: dict):
    try:
        # Validar que cumple el formato FHIR
        encounter = Encounter.model_validate(encounter_dict)
    except Exception as e:
        print("Error validando encounter:", e)
        return f"errorValidating: {str(e)}", None

    # Convertir a diccionario limpio y guardar en MongoDB
    validated_encounter_json = encounter.model_dump()
    result = collection.insert_one(validated_encounter_json)

    if result:
        inserted_id = str(result.inserted_id)
        return "success", inserted_id
    else:
        return "errorInserting", None
