from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.database.database import db
from app.database.database import Prescription, PrescriptionMedication
from datetime import datetime

def create_prescription(prescription_data: dict):
    try:
        # Create prescription
        prescription_query = Prescription.create(
            appointment_id=prescription_data.appointment_id,
            doctor_id=prescription_data.doctor_id,
            patient_id=prescription_data.patient_id,
            diagnosis=prescription_data.diagnosis,
            notes=prescription_data.notes,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.execute_query(prescription_query)
        prescription_id = db.get_last_insert_id()

        # Create prescription medications
        for medication in prescription_data.medications:
            medication_query = PrescriptionMedication.create(
                prescription_id=prescription_id,
                medication_name=medication.medication_name,
                dosage=medication.dosage,
                frequency=medication.frequency,
                duration=medication.duration,
                instructions=medication.instructions
            )
            db.execute_query(medication_query)

        return JSONResponse(
            content={"message": "Prescription created successfully", "prescription_id": prescription_id},
            status_code=201
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating prescription: {str(e)}"
        )

def get_prescription_by_id(prescription_id: int, current_user: dict):
    try:
        # Get prescription
        prescription_query = Prescription.find(prescription_id=prescription_id)
        db.execute_query(prescription_query, params=(prescription_id,))
        prescription = db.fetch_one()
        
        if not prescription:
            raise HTTPException(status_code=404, detail="Prescription not found")

        # Check access rights
        if current_user["role"] == "patient" and current_user["user_id"] != prescription[3]:
            raise HTTPException(status_code=403, detail="Access denied")

        # Get medications
        medications_query = PrescriptionMedication.find(prescription_id=prescription_id)
        db.execute_query(medications_query, params=(prescription_id,))
        medications = db.fetch_all()

        prescription_data = {
            "prescription_id": prescription[0],
            "appointment_id": prescription[1],
            "doctor_id": prescription[2],
            "patient_id": prescription[3],
            "diagnosis": prescription[4],
            "notes": prescription[5],
            "created_at": prescription[6].isoformat(),
            "updated_at": prescription[7].isoformat(),
            "medications": [
                {
                    "medication_id": med[0],
                    "medication_name": med[2],
                    "dosage": med[3],
                    "frequency": med[4],
                    "duration": med[5],
                    "instructions": med[6]
                }
                for med in medications
            ]
        }

        return JSONResponse(content=prescription_data, status_code=200)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving prescription: {str(e)}"
        )

def get_prescriptions_by_doctor(doctor_id: int):
    try:
        prescription_query = Prescription.find(doctor_id=doctor_id)
        db.execute_query(prescription_query, params=(doctor_id,))
        prescriptions = db.fetch_all()

        if not prescriptions:
            return JSONResponse(content={"prescriptions": []}, status_code=200)

        prescriptions_data = []
        for prescription in prescriptions:
            medications_query = PrescriptionMedication.find(prescription_id=prescription[0])
            db.execute_query(medications_query, params=(prescription[0],))
            medications = db.fetch_all()

            prescriptions_data.append({
                "prescription_id": prescription[0],
                "appointment_id": prescription[1],
                "doctor_id": prescription[2],
                "patient_id": prescription[3],
                "diagnosis": prescription[4],
                "notes": prescription[5],
                "created_at": prescription[6].isoformat(),
                "updated_at": prescription[7].isoformat(),
                "medications": [
                    {
                        "medication_id": med[0],
                        "medication_name": med[2],
                        "dosage": med[3],
                        "frequency": med[4],
                        "duration": med[5],
                        "instructions": med[6]
                    }
                    for med in medications
                ]
            })

        return JSONResponse(
            content={"prescriptions": prescriptions_data},
            status_code=200
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving prescriptions: {str(e)}"
        )

def get_prescriptions_by_patient(patient_id: int):
    try:
        prescription_query = Prescription.find(patient_id=patient_id)
        db.execute_query(prescription_query, params=(patient_id,))
        prescriptions = db.fetch_all()

        if not prescriptions:
            return JSONResponse(content={"prescriptions": []}, status_code=200)

        prescriptions_data = []
        for prescription in prescriptions:
            medications_query = PrescriptionMedication.find(prescription_id=prescription[0])
            db.execute_query(medications_query, params=(prescription[0],))
            medications = db.fetch_all()

            prescriptions_data.append({
                "prescription_id": prescription[0],
                "appointment_id": prescription[1],
                "doctor_id": prescription[2],
                "patient_id": prescription[3],
                "diagnosis": prescription[4],
                "notes": prescription[5],
                "created_at": prescription[6].isoformat(),
                "updated_at": prescription[7].isoformat(),
                "medications": [
                    {
                        "medication_id": med[0],
                        "medication_name": med[2],
                        "dosage": med[3],
                        "frequency": med[4],
                        "duration": med[5],
                        "instructions": med[6]
                    }
                    for med in medications
                ]
            })

        return JSONResponse(
            content={"prescriptions": prescriptions_data},
            status_code=200
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving prescriptions: {str(e)}"
        )

def update_prescription(prescription_id: int, prescription_data: dict, doctor_id: int):
    try:
        # Check if prescription exists and belongs to the doctor
        check_query = Prescription.find(prescription_id=prescription_id)
        db.execute_query(check_query, params=(prescription_id,))
        prescription = db.fetch_one()
        
        if not prescription:
            raise HTTPException(status_code=404, detail="Prescription not found")
            
        if prescription[2] != doctor_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Update prescription
        update_query = Prescription.update(
            prescription_id=prescription_id,
            **prescription_data.dict(exclude_unset=True)
        )
        db.execute_query(update_query)

        return JSONResponse(
            content={"message": "Prescription updated successfully"},
            status_code=200
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating prescription: {str(e)}"
        )

def delete_prescription(prescription_id: int, doctor_id: int):
    try:
        # Check if prescription exists and belongs to the doctor
        check_query = Prescription.find(prescription_id=prescription_id)
        db.execute_query(check_query, params=(prescription_id,))
        prescription = db.fetch_one()
        
        if not prescription:
            raise HTTPException(status_code=404, detail="Prescription not found")
            
        if prescription[2] != doctor_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Delete medications first
        delete_medications_query = f"DELETE FROM {PrescriptionMedication.table_name} WHERE prescription_id = %s"
        db.execute_query(delete_medications_query, params=(prescription_id,))

        # Delete prescription
        delete_query = f"DELETE FROM {Prescription.table_name} WHERE prescription_id = %s"
        db.execute_query(delete_query, params=(prescription_id,))

        return JSONResponse(
            content={"message": "Prescription deleted successfully"},
            status_code=200
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting prescription: {str(e)}"
        )