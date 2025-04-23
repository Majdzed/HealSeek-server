from fastapi import Response , HTTPException , Request
from fastapi.responses import JSONResponse
from app.database.database import Rating as rt, db , Doctor as doc , Patient as pat ,User as us
from app.models.rating import Rating

def get_all_ratings():
    try : 
        db.execute_query("SELECT * FROM ratings;")
        result = db.fetch_all()
        ratings_data = [{"rating_id": rating[0] ,"rating_score" : rating[1] ,"review_text" : rating[2], "doctor_id": rating[3], "patient_id": rating[4]} for rating in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while fetching ratings : " + str(e))
    if not ratings_data:
        raise HTTPException(status_code=404, detail="No ratings found")
    return JSONResponse(content=ratings_data, status_code=200)

def add_rating(request : Request,rating : Rating):
    try:
        existing_doctor = doc.find(user_id=rating.doctor_id)
        db.execute_query(existing_doctor, params=(rating.doctor_id,))
        existing_doctor = db.fetch_one()
        if not existing_doctor:
            raise HTTPException(status_code=404, detail="Doctor ID is wrong")
        
        existing_patient = us.find(user_id=rating.patient_id)
        db.execute_query(existing_patient, params=(rating.patient_id,))
        existing_patient = db.fetch_one()
        if not existing_patient:
            raise HTTPException(status_code=404, detail="Patient ID is wrong")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while checking doctor or patient ID : " + str(e))
    try:
        existing_rate = rt.find(patient_id=rating.patient_id, doctor_id=rating.doctor_id)
        db.execute_query(existing_rate, params=(rating.patient_id, rating.doctor_id))
        existing_rate = db.fetch_one()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while finding rating" + str(e))
    if existing_rate :
        raise HTTPException(status_code=400, detail="You've already rated this doctor")#You can't spam rates lil nigga
    if rating.rating_score> 5 or rating.rating_score<0 : 
        raise HTTPException(status_code=400 , detail="you can't put more than 5 or less than 0 in a rating!!!" )
    try:
        rating_query = rt.insert(rating_score=rating.rating_score, review_text=rating.review_text, doctor_id=rating.doctor_id, patient_id=rating.patient_id)
        print(rating)
        db.execute_query(rating_query)
        return JSONResponse(content=rating.dict(), status_code=200)
    except Exception as e: 
        return HTTPException(status_code=500 , detail="error : "+str(e))

def get_rating_by_id(rating_id : int):
    rating_query = rt.find(rating_id = rating_id)
    db.execute_query(rating_query,params=(rating_id,))
    rating = db.fetch_one()
    print(rating)
    if not rating:
        raise HTTPException(status_code=404, detail="No rating found")
    rating = {"rating_id": rating[0] ,"rating_score" : rating[1] ,"review_text" : rating[2], "doctor_id": rating[3], "patient_id": rating[4]}

    return JSONResponse(content=rating , status_code=200)

def update_rating(request : Request,rating_id : int , updated_rating : dict):
    user_id = request.state.user
    try : 
        found_rating = rt.find(rating_id=rating_id)
        db.execute_query(found_rating, params=(rating_id,))
        rating = db.fetch_one()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while finding rating")
    
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    if rating[4] != user_id:
        raise HTTPException(status_code=403, detail="You can't update someone else's rating")
    if updated_rating.get("rating_score"):
        if updated_rating["rating_score"]> 5 or updated_rating["rating_score"]<0 : 
            raise HTTPException(status_code=400 , detail="you can't put more than 5 or less than 0 in a rating!!!")
    
    try:
        update_rating_query = rt.update(**updated_rating, rating_id=rating_id)
        print(update_rating_query)
        db.execute_query(update_rating_query,params=(*[value for _, value in updated_rating.items()], rating_id))
        return JSONResponse(content=updated_rating, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="internal error : "+ str(e))
    
def delete_rating(rating_id : int):
    try:
        found_rating = rt.find(rating_id=rating_id)
        db.execute_query(found_rating, params=(rating_id,))
        rating = db.fetch_one()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while finding rating")
    
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    try:
        delete_rating_query = rt.delete(rating_id=rating_id)
        db.execute_query(delete_rating_query, params=(rating_id,))
        return JSONResponse(content={"message": "Rating deleted successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="internal error : "+ str(e))
    

def get_ratings_by_doctor(doctor_id: int):
    try:
        db.execute_query(f"SELECT * FROM ratings JOIN users ON ratings.patient_id = users.user_id WHERE doctor_id = {doctor_id}")
        result = db.fetch_all()
        print(result)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"No ratings found for doctor {doctor_id}")
        print(result)
        ratings_data = [
            {
                "rating_id": rating[0],
                "rating_score": rating[1],
                "review_text": rating[2],
                "doctor_id": rating[3],
                "patient_id": rating[4],
                "user" : {
                    "name" : rating[6],
                    "profile_picture_url" : rating[13]
                }
            } for rating in result
        ]
        print(ratings_data)
        return JSONResponse(content=ratings_data, status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error while fetching ratings for doctor: {str(e)}"
        )

def get_ratings_by_patient(request: Request, patient_id: int):
    # Verify the requesting user matches the patient_id or is an admin
    user_id = request.state.user
    try:
        # First check if the patient exists
        existing_patient = us.find(user_id=patient_id)
        db.execute_query(existing_patient, params=(patient_id,))
        patient = db.fetch_one()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
            
        # Get the ratings
        query = rt.find(patient_id=patient_id)
        db.execute_query(query, params=(patient_id,))
        result = db.fetch_all()
        
        if not result:
            raise HTTPException(status_code=404, detail=f"No ratings found for patient {patient_id}")
            
        ratings_data = [
            {
                "rating_id": rating[0],
                "rating_score": rating[1],
                "review_text": rating[2],
                "doctor_id": rating[3],
                "patient_id": rating[4]
            } for rating in result
        ]
        return JSONResponse(content=ratings_data, status_code=200)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error while fetching ratings for patient: {str(e)}"
        )