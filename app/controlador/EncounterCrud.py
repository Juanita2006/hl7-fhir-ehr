import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from bson import ObjectId
from fhir.resources.encounter import Encounter
from fhir.resources.condition import Condition
from fhir.resources.servicerequest import ServiceRequest
from fhir.resources.medicationrequest import MedicationRequest

class EncounterCRUD:
    def __init__(self):
        self.client = None
        self.db = None
        self.collections = {}
        self._connect()

    def _connect(self):
        """Establece conexión con MongoDB y configura colecciones"""
        try:
            self.client = MongoClient(
                os.getenv("MONGO_URI", "mongodb://localhost:27017/"),
                serverSelectionTimeoutMS=5000,
                socketTimeoutMS=30000,
                connectTimeoutMS=30000,
                retryWrites=True
            )
            
            # Verificar conexión
            self.client.admin.command('ping')
            self.db = self.client["JYI"]
            
            # Configurar colecciones
            self.collections = {
                "encounters": self.db["encounters"],
                "conditions": self.db["conditions"],
                "servicerequests": self.db["servicerequests"],
                "medicationrequests": self.db["medicationrequests"]
            }
            
            # Crear índices
            self._create_indexes()
            print("✅ Conexión a MongoDB establecida correctamente")
            
        except ConnectionFailure as e:
            print(f"❌ Error crítico de conexión: {str(e)}")
            raise

    def _create_indexes(self):
        """Crea índices necesarios para optimizar consultas"""
        try:
            # Índice para búsqueda por paciente en encounters
            self.collections["encounters"].create_index(
                [("subject.reference", 1)]
            )
            
            # Índice para búsqueda por encounter en recursos relacionados
            for collection in ["conditions", "servicerequests", "medicationrequests"]:
                self.collections[collection].create_index(
                    [("encounter.reference", 1)]
                )
                
        except OperationFailure as e:
            print(f"⚠️ Error creando índices: {str(e)}")

    def WriteEncounter(self, encounter_dict: dict):
        """Guarda un recurso Encounter validado"""
        try:
            print("📤 Validando y guardando Encounter...")
            encounter = Encounter.model_validate(encounter_dict)
            result = self.collections["encounters"].insert_one(encounter.model_dump())
            print(f"✅ Encounter guardado con ID: {result.inserted_id}")
            return "success", str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error al guardar Encounter: {str(e)}")
            return f"error: {str(e)}", None

    def WriteCondition(self, condition_dict: dict):
        """Guarda un recurso Condition validado"""
        try:
            condition = Condition.model_validate(condition_dict)
            result = self.collections["conditions"].insert_one(condition.model_dump())
            return "success", str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error al guardar Condition: {str(e)}")
            return f"error: {str(e)}", None

    def WriteServiceRequest(self, service_request_dict: dict):
        """Guarda un recurso ServiceRequest validado"""
        try:
            service_request = ServiceRequest.model_validate(service_request_dict)
            result = self.collections["servicerequests"].insert_one(service_request.model_dump())
            return "success", str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error al guardar ServiceRequest: {str(e)}")
            return f"error: {str(e)}", None

    def WriteMedicationRequest(self, medication_request_dict: dict):
        """Guarda un recurso MedicationRequest validado"""
        try:
            medication_request = MedicationRequest.model_validate(medication_request_dict)
            result = self.collections["medicationrequests"].insert_one(medication_request.model_dump())
            return "success", str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error al guardar MedicationRequest: {str(e)}")
            return f"error: {str(e)}", None

    def WriteEncounterWithResources(self, encounter_data: dict):
        """
        Guarda un Encounter con sus recursos asociados de forma transaccional
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
        session = None
        try:
            # Validación inicial
            if not encounter_data.get("encounter"):
                return "error: Missing encounter data", None

            # Iniciar transacción
            session = self.client.start_session()
            session.start_transaction()
            
            print("🚀 Iniciando transacción para guardar encounter con recursos...")
            
            # 1. Guardar Encounter
            encounter = Encounter.model_validate(encounter_data["encounter"])
            encounter_result = self.collections["encounters"].insert_one(
                encounter.model_dump(), 
                session=session
            )
            encounter_id = str(encounter_result.inserted_id)
            print(f"📝 Encounter guardado con ID: {encounter_id}")

            # 2. Procesar recursos asociados
            resources = [
                ("condition", self.WriteCondition),
                ("service_request", self.WriteServiceRequest),
                ("medication_request", self.WriteMedicationRequest)
            ]

            errors = []
            for resource_name, writer in resources:
                if resource_name in encounter_data:
                    data = encounter_data[resource_name].copy()
                    data["encounter"] = {"reference": f"Encounter/{encounter_id}"}
                    
                    # Validar y preparar recurso
                    resource = {
                        "condition": Condition,
                        "service_request": ServiceRequest,
                        "medication_request": MedicationRequest
                    }[resource_name].model_validate(data)
                    
                    # Insertar en transacción
                    collection_name = resource_name + "s"  # Pluralizar
                    self.collections[collection_name].insert_one(
                        resource.model_dump(),
                        session=session
                    )
                    print(f"✅ {resource_name.capitalize()} guardado correctamente")

            # Confirmar transacción si todo fue bien
            session.commit_transaction()
            print("🎉 Transacción completada con éxito")
            return "success", encounter_id

        except Exception as e:
            # Revertir transacción en caso de error
            if session:
                session.abort_transaction()
                print("🔴 Transacción abortada debido a errores")
            
            print(f"❌ Error en WriteEncounterWithResources: {str(e)}")
            return f"error: {str(e)}", None
        
        finally:
            if session:
                session.end_session()

# Instancia global para usar en la aplicación
encounter_crud = EncounterCRUD()
