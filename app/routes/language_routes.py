from fastapi import APIRouter ,Depends ,Request
from app.controllers.language_controllers import get_all_languages as get_all ,get_language_by_id , get_language_by_name , add_language , delete_language , update_language
from app.controllers.language_controllers import add_language_to_doctor_by_id , add_language_to_doctor_by_name , get_all_languages_of_doctor , get_all_doctors_using_language , delete_language_from_doctor ,get_all_languages_doctors
from app.models.language import Language , DoctorLanguage , DoctorLanguage2
from app.routes.user_routes import resolve_user


router = APIRouter()

@router.get('/all')
def get_all_languages():
    return get_all()

@router.get('/get_by_id/{language_id}')
def get_language_using_id(language_id:int):
    return get_language_by_id(language_id)

@router.get('/get_by_name/{language_name}')
def get_language_using_name(language_name:str):
    return get_language_by_name(language_name)

@router.post('/add' , dependencies=[Depends(resolve_user(allowed_roles=["admin"]))])
def add_lang(language:Language):
    return add_language(language)

@router.delete('/delete/{language_id}' , dependencies=[Depends(resolve_user(allowed_roles=["admin"]))])
def delete_lang(language_id:int):
    return delete_language(language_id)

@router.put('/update/{language_id}' , dependencies=[Depends(resolve_user(allowed_roles=["admin"]))])
def update_lang(language_id:int , language_data:dict):
    return update_language(language_id , language_data)

@router.post('/doctor/add_by_id' , dependencies=[Depends(resolve_user(allowed_roles=["doctor"]))])
def add_lang_to_doc_using_id(language:DoctorLanguage):
    return add_language_to_doctor_by_id(language)

@router.post('/doctor/add_by_name' , dependencies=[Depends(resolve_user(allowed_roles=["doctor"]))])
def add_lang_to_doc_using_name(language:DoctorLanguage2):
    return add_language_to_doctor_by_name(language)

@router.get('/doctor/all_languages/{doctor_id}' ,dependencies=[Depends(resolve_user(allowed_roles=["doctor"]))])
def get_all_languages_of_doc(request : Request):
    doctor_id = request.state.user
    return get_all_languages_of_doctor(doctor_id)

@router.get('/doctor/all_doctors/{language_id}')
def get_all_docs_of_language(language_id:int):
    return get_all_doctors_using_language(language_id)

@router.delete('/doctor/delete_language' , dependencies=[Depends(resolve_user(allowed_roles=["doctor"]))])
def delete_lang_from_doc(language:DoctorLanguage):
    return delete_language_from_doctor(language)

@router.get('/doctor/all_languages_doctors')
def get_all_languages_docs():
    return get_all_languages_doctors()
