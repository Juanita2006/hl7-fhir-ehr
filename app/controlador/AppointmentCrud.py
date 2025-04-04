from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.appointment import Appointment

# Conexión a la base de datos y colección para citas
collection = connect_to_mongodb("JYI", "2626")  # Reemplaza con tu DB y colección reales si cambia

def WriteAppointment(appointment_dict: dict):
    try:
        # Validar el recurso usando el modelo FHIR
        app = Appointment.model_validate(appointment_dict)
    except Exception as e:
        return f"errorValidating: {str(e)}", None

    validated_appointment_json = app.model_dump()

    try:
        result = collection.insert_one(validated_appointment_json)
        if result:
            inserted_id = str(result.inserted_id)
            return "success"

