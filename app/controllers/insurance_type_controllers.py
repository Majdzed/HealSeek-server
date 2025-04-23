from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.models.insurance_type import Insurance , DoctorInsurance , DoctorInsurance2
from app.database.database import InsuranceType as it , db , DoctorInsurance as DocIn , Doctor as doc


def get_all_insurance_types():
    db.execute_query("SELECT * FROM insurance_types;")
    insurances = db.fetch_all()
    if not insurances:
        raise HTTPException(status_code=404, detail="No insurance types found")
    insurance_data = [{"insurance_type_id": insurance[0] ,"type_name" : insurance[1]} for insurance in insurances]
    return JSONResponse(content=insurance_data, status_code=200)


def add_insurance_type(insurance : Insurance):
    try:
        existing_insurance = it.find(type_name=insurance.type_name)
        db.execute_query(existing_insurance, params=(insurance.type_name,))
        existing_insurance = db.fetch_one()
        if existing_insurance:
            raise HTTPException(status_code=400, detail="Insurance type already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while checking insurance type : " + str(e))
    try:
        insurance_query = it.insert(type_name=insurance.type_name)
        db.execute_query(insurance_query)
        return JSONResponse(content=insurance.dict(), status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while adding insurance type : " + str(e))
    
def update_insurance_type(insurance_id:int , insurance_data:dict):
    existing_insurance = it.find(insurance_type_id=insurance_id)
    db.execute_query(existing_insurance, params=(insurance_id,))
    existing_insurance = db.fetch_one()
    if not existing_insurance:
        raise HTTPException(status_code=404, detail="Insurance type not found")
    try:
        insurance_query = it.update(type_name=insurance_data['type_name'] , insurance_type_id=existing_insurance[0])
        db.execute_query(insurance_query , params=(insurance_data['type_name'],existing_insurance[0]))
        return JSONResponse(content=insurance_data, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while updating insurance type : " + str(e))

def get_insurance_type_by_id(insurance_id:int):
    existing_insurance = it.find(insurance_type_id=insurance_id)
    db.execute_query(existing_insurance, params=(insurance_id,))
    existing_insurance = db.fetch_one()
    if not existing_insurance:
        raise HTTPException(status_code=404, detail="Insurance type not found")
    insurance_data = {"insurance_type_id": existing_insurance[0] ,"type_name" : existing_insurance[1]}
    return JSONResponse(content=insurance_data, status_code=200)

def get_insurance_type_by_name(insurance_name:str):
    existing_insurance = it.find(type_name=insurance_name)
    db.execute_query(existing_insurance, params=(insurance_name,))
    existing_insurance = db.fetch_one()
    if not existing_insurance:
        raise HTTPException(status_code=404, detail="Insurance type not found")
    insurance_data = {"insurance_type_id": existing_insurance[0] ,"type_name" : existing_insurance[1]}
    return JSONResponse(content=insurance_data, status_code=200)

def delete_insurance_type(insurance_id : int):
    existing_insurance = it.find(insurance_type_id=insurance_id)
    db.execute_query(existing_insurance, params=(insurance_id,))
    existing_insurance = db.fetch_one()
    if not existing_insurance:
        raise HTTPException(status_code=404, detail="Insurance type not found")
    try:
        insurance_query = it.delete(insurance_type_id=insurance_id)
        db.execute_query(insurance_query , params=(insurance_id,))
        return JSONResponse(content={"message" : "Insurance type deleted successfully"} , status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while deleting insurance type : " + str(e))
    
def add_insurance_to_doctor_using_insurance_id(DoctorInsurance : DoctorInsurance):
    doctor_id = DoctorInsurance.doctor_id
    insurance_id = DoctorInsurance.insurance_type_id
    existing_doctor = doc.find(user_id=doctor_id)
    db.execute_query(existing_doctor, params=(doctor_id,))
    if not db.fetch_one():
        raise HTTPException(status_code=404, detail="Doctor Id incorrect")
    existing_insurance = it.find(insurance_type_id=insurance_id)
    db.execute_query(existing_insurance, params=(insurance_id,))
    if not db.fetch_one():
        raise HTTPException(status_code=404, detail="Insurance type ID Incorrect")
    
    existing_doc_i = DocIn.find(doctor_id=DoctorInsurance.doctor_id , insurance_type_id=DoctorInsurance.insurance_type_id)
    db.execute_query(existing_doc_i, params=(DoctorInsurance.doctor_id , DoctorInsurance.insurance_type_id))
    if db.fetch_one():
        raise HTTPException(status_code=400, detail="Insurance type already added to doctor")
    try:
        insurance_query = DocIn.insert(doctor_id=DoctorInsurance.doctor_id , insurance_type_id=DoctorInsurance.insurance_type_id)
        db.execute_query(insurance_query)
        return JSONResponse(content=DoctorInsurance.dict(), status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while adding insurance type to doctor : " + str(e))
    
def add_insurance_to_doctor_using_insurance_name(insurance : DoctorInsurance2):
        insurance_name = insurance.insurance_type_name
        doctor_id = insurance.doctor_id
        
        existing_doctor =doc.find(user_id=doctor_id)
        db.execute_query(existing_doctor, params=(doctor_id,))
        if not db.fetch_one():
            raise HTTPException(status_code=404, detail="Doctor Id incorrect")
        
        existing_insurance = it.find(type_name=insurance_name)
        db.execute_query(existing_insurance, params=(insurance_name,))
        existing_insurance = db.fetch_one()
        if not existing_insurance:
            raise HTTPException(status_code=404, detail="Insurance type ID incorrect")
        existing_doc_i = DocIn.find(doctor_id=doctor_id , insurance_type_id=existing_insurance[0])
        db.execute_query(existing_doc_i, params=(doctor_id , existing_insurance[0]))
        if db.fetch_one():
            raise HTTPException(status_code=400, detail="Insurance type already added to doctor")
        try:
            insurance_query = DocIn.insert(doctor_id=doctor_id , insurance_type_id=existing_insurance[0])
            db.execute_query(insurance_query)
            return JSONResponse(content={"doctor_id" : doctor_id , "insurance_type_id" : existing_insurance[0]} , status_code=200)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error while adding insurance type to doctor : " + str(e))
        
    
def get_all_insurance_types_of_doctor(doctor_id:int):
    db.execute_query("SELECT * FROM doctor_insurance WHERE doctor_id = %s;" , params=(doctor_id,))
    insurances = db.fetch_all()
    if not insurances:
        raise HTTPException(status_code=404, detail="No insurance types found for this doctor")
    insurance_data = [{"doctor_id": insurance[0] ,"insurance_type_id" : insurance[1]} for insurance in insurances]
    return JSONResponse(content=insurance_data, status_code=200)

def delete_insurance_from_doctor(insurance:DoctorInsurance):
    doctor_id = insurance.doctor_id
    insurance_id = insurance.insurance_type_id
    existing_doc_i = DocIn.find(doctor_id=doctor_id , insurance_type_id=insurance_id)
    db.execute_query(existing_doc_i, params=(doctor_id , insurance_id))
    existing_doc_i = db.fetch_one()
    if not existing_doc_i:
        raise HTTPException(status_code=404, detail="Insurance type not found for this doctor")
    try:
        insurance_query = DocIn.delete(doctor_id=doctor_id , insurance_type_id=insurance_id)
        db.execute_query(insurance_query , params=(doctor_id , insurance_id))
        return JSONResponse(content={"message" : "Insurance type deleted successfully"} , status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while deleting doctor's insurance type : " + str(e))
    
    
    
def get_all_doctors_of_insurance(insurance_id:int):
    existing_insurance = it.find(insurance_type_id=insurance_id)
    db.execute_query(existing_insurance, params=(insurance_id,))
    existing_insurance = db.fetch_one()
    if not existing_insurance:
        raise HTTPException(status_code=404, detail="Insurance type doesn't exist")
    
    db.execute_query("SELECT * FROM doctor_insurance WHERE insurance_type_id = %s;" , params=(insurance_id,))
    doctors = db.fetch_all()
    if not doctors:
        raise HTTPException(status_code=404, detail="No doctors found for this insurance type")
    doctor_data = [{"doctor_id": doctor[0] ,"insurance_type_id" : doctor[1]} for doctor in doctors]
    return JSONResponse(content=doctor_data, status_code=200)

    
def get_all_doctors_of_insurance_type_by_name(insurance_name:str):
    existing_insurance = it.find(type_name=insurance_name)
    db.execute_query(existing_insurance, params=(insurance_name,))
    existing_insurance = db.fetch_one()
    if not existing_insurance:
        raise HTTPException(status_code=404, detail="Insurance type not found")
    db.execute_query("SELECT * FROM doctor_insurance WHERE insurance_type_id = %s;" , params=(existing_insurance[0],))
    doctors = db.fetch_all()
    if not doctors:
        raise HTTPException(status_code=404, detail="No doctors found for this insurance type")
    doctor_data = [{"doctor_id": doctor[0] ,"insurance_type_id" : doctor[1]} for doctor in doctors]
    return JSONResponse(content=doctor_data, status_code=200)

def get_all_insurances_of_doctors():
    db.execute_query("SELECT * FROM doctor_insurance;")
    insurances = db.fetch_all()
    if not insurances:
        raise HTTPException(status_code=404, detail="No insurance types found for any doctor")
    insurance_data = [{"doctor_id": insurance[0] ,"insurance_type_id" : insurance[1]} for insurance in insurances]
    return JSONResponse(content=insurance_data, status_code=200)
