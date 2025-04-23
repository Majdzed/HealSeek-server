from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.models.language import Language , DoctorLanguage , DoctorLanguage2
from app.database.database import  Language as ln , db , DoctorLanguage as DocLang , Doctor as doc


def get_all_languages():
    db.execute_query("SELECT * FROM languages;")
    languages = db.fetch_all()
    if not languages:
        raise HTTPException(status_code=404, detail="No languages found")
    language_data = [{"language_id": language[0] ,"language_name" : language[1]} for language in languages]
    return JSONResponse(content=language_data, status_code=200)

def get_language_by_id(language_id:int):
    existing_language = ln.find(language_id=language_id)
    db.execute_query(existing_language, params=(language_id,))
    existing_language = db.fetch_one()
    if not existing_language:
        raise HTTPException(status_code=404, detail="Language not found")
    language_data = {"language_id": existing_language[0] ,"language_name" : existing_language[1]}
    return JSONResponse(content=language_data, status_code=200)

def get_language_by_name(language_name:str):
    existing_language = ln.find(language_name=language_name)
    db.execute_query(existing_language, params=(language_name,))
    existing_language = db.fetch_one()
    if not existing_language:
        raise HTTPException(status_code=404, detail="Language not found")
    language_data = {"language_id": existing_language[0] ,"language_name" : existing_language[1]}
    return JSONResponse(content=language_data, status_code=200)

def add_language(language:Language):
    try:
        existing_language = ln.find(language_name=language.language_name)
        db.execute_query(existing_language, params=(language.language_name,))
        existing_language = db.fetch_one()
        if existing_language:
            raise HTTPException(status_code=400, detail="Language already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while checking language : " + str(e))
    try:
        language_query = ln.insert(language_name=language.language_name)
        db.execute_query(language_query)
        return JSONResponse(content=language.dict(), status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while adding language : " + str(e))
    
def update_language(language_id:int , language_data:dict):
    existing_language = ln.find(language_id=language_id)
    db.execute_query(existing_language, params=(language_id,))
    existing_language = db.fetch_one()
    if not existing_language:
        raise HTTPException(status_code=404, detail="Language not found")
    if 'language_name' not in language_data:
        raise HTTPException(status_code=400, detail="Language name not provided,nothing to update")
    duplicate_name_language = ln.find(language_name=language_data['language_name'])
    db.execute_query(duplicate_name_language, params=(language_data['language_name'],))
    if db.fetch_one():
        raise HTTPException(status_code=400, detail="Language with this name already exists")
    try:
        language_query = ln.update(language_name=language_data['language_name'] , language_id=existing_language[0])
        db.execute_query(language_query , params=(language_data['language_name'],existing_language[0]))
        return JSONResponse(content=language_data, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while updating language : " + str(e))


def delete_language(language_id : int):
    existing_language = ln.find(language_id=language_id)
    db.execute_query(existing_language, params=(language_id,))
    existing_language = db.fetch_one()
    if not existing_language:
        raise HTTPException(status_code=404, detail="Language not found")
    try:
        language_query = ln.delete(language_id=language_id)
        db.execute_query(language_query , params=(language_id,))
        return JSONResponse(content={"message":"Language deleted successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while deleting language : " + str(e))
    
def add_language_to_doctor_by_id(language:DoctorLanguage):
    try:
        existing_language = ln.find(language_id=language.language_id)
        db.execute_query(existing_language, params=(language.language_id,))
        existing_language = db.fetch_one()
        if not existing_language:
            raise HTTPException(status_code=404, detail="Language not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while checking language : " + str(e))
    try:
        existing_doctor = doc.find(user_id=language.doctor_id)
        db.execute_query(existing_doctor, params=(language.doctor_id,))
        existing_doctor = db.fetch_one()
        if not existing_doctor:
            raise HTTPException(status_code=400, detail="Incorrect doctor ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while checking doctor's existence : " + str(e))
    try:
        existing_doctor_language = DocLang.find(doctor_id=language.doctor_id , language_id=language.language_id)
        db.execute_query(existing_doctor_language, params=(language.doctor_id,language.language_id))
        existing_doctor_language = db.fetch_one()
        if existing_doctor_language:
            raise HTTPException(status_code=400, detail="Language already added to doctor")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while checking doctor language : " + str(e))
    try:
        language_query = DocLang.insert(doctor_id=language.doctor_id , language_id=language.language_id)
        db.execute_query(language_query)
        return JSONResponse(content=language.dict(), status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while adding language to doctor : " + str(e))

def add_language_to_doctor_by_name(language: DoctorLanguage2) -> JSONResponse:
    try:
        db.execute_query(ln.find(language_name=language.language_name), params=(language.language_name,))
        existing_language = db.fetch_one()
        if not existing_language:
            raise HTTPException(status_code=404, detail=f"Language '{language.language_name}' not found")

        db.execute_query(doc.find(user_id=language.doctor_id), params=(language.doctor_id,))
        if not db.fetch_one():
            raise HTTPException(status_code=404, detail=f"Doctor with ID {language.doctor_id} not found")

        language_id = existing_language[0]
        db.execute_query(
            DocLang.find(doctor_id=language.doctor_id, language_id=language_id),
            params=(language.doctor_id, language_id)
        )
        if db.fetch_one():
            raise HTTPException(
                status_code=400, 
                detail=f"Language '{language.language_name}' already assigned to doctor {language.doctor_id}"
            )

        db.execute_query(DocLang.insert(doctor_id=language.doctor_id, language_id=language_id))
        
        response_data = {
            "doctor_id": language.doctor_id,
            "language_name": language.language_name,
            "language_id": language_id
        }
        return JSONResponse(content=response_data, status_code=201)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def get_all_languages_of_doctor(doctor_id:int):
    try:
        existing_doctor = doc.find(user_id=doctor_id)
        db.execute_query(existing_doctor, params=(doctor_id,))
        existing_doctor = db.fetch_one()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while checking doctor : " + str(e))
    if not existing_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    try:
        db.execute_query("SELECT * FROM doctor_languages WHERE doctor_id=%s;", params=(doctor_id,))
        doctor_languages = db.fetch_all()
        if not doctor_languages:
            raise HTTPException(status_code=404, detail="No languages found for doctor")
        language_data = [{"doctor_id": language[0] ,"language_id" : language[1]} for language in doctor_languages]
        return JSONResponse(content=language_data, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while fetching doctor languages : " + str(e))

def get_all_doctors_using_language(language_id : int):
    existing_language = ln.find(language_id=language_id)
    db.execute_query(existing_language, params=(language_id,))
    if not db.fetch_one():
        raise HTTPException(status_code=404, detail="Language not found")
    try:
        db.execute_query("SELECT * FROM doctor_languages WHERE language_id=%s;", params=(language_id,))
        doctor_languages = db.fetch_all()
        if not doctor_languages:
            raise HTTPException(status_code=404, detail="No doctors found for this language")
        doctor_data = [{"doctor_id": language[0] ,"language_id" : language[1]} for language in doctor_languages]
        return JSONResponse(content=doctor_data, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while fetching doctors using language : " + str(e))

def delete_language_from_doctor(language:DoctorLanguage):
    try:
        existing_language = ln.find(language_id=language.language_id)
        db.execute_query(existing_language, params=(language.language_id,))
        existing_language = db.fetch_one()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while checking language : " + str(e))
    if not existing_language:
        raise HTTPException(status_code=404, detail="Language not found")
    try:
        existing_doctor = doc.find(user_id=language.doctor_id)
        db.execute_query(existing_doctor, params=(language.doctor_id,))
        existing_doctor = db.fetch_one()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error checking doctor existence : " + str(e))
    if not existing_doctor:
        raise HTTPException(status_code=400, detail="Incorrect doctor ID")
    try:
        existing_doctor_language = DocLang.find(doctor_id=language.doctor_id , language_id=language.language_id)
        db.execute_query(existing_doctor_language, params=(language.doctor_id,language.language_id))
        existing_doctor_language = db.fetch_one()
        if not existing_doctor_language:
            raise HTTPException(status_code=400, detail="Language not added to doctor")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while checking doctor language : " + str(e))
    try:
        language_query = DocLang.delete(doctor_id=language.doctor_id , language_id=language.language_id)
        db.execute_query(language_query , params=(language.doctor_id,language.language_id))
        return JSONResponse(content={"message":"Language deleted from doctor successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while deleting language from doctor : " + str(e))
        
def get_all_languages_doctors():
    db.execute_query("SELECT * FROM doctor_languages;")
    doctor_languages = db.fetch_all()
    if not doctor_languages:
        raise HTTPException(status_code=404, detail="No languages found for doctors")
    doctor_language_data = [{"doctor_id": doctor_language[0] ,"language_id" : doctor_language[1]} for doctor_language in doctor_languages]
    return JSONResponse(content=doctor_language_data, status_code=200)

                            