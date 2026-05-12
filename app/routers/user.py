from fastapi import APIRouter, HTTPException, status
from schemas.user import User, UserCreate, UserUpdate
from database import users_db

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[User])
async def get_users():
    return list(users_db.values())

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    new_id = max(users_db.keys()) + 1 if users_db else 1
    user_dict = user_data.model_dump()
    user_dict["id"] = new_id
    del user_dict["password"] 
    users_db[new_id] = user_dict
    return user_dict

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user_data: UserUpdate):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_user = users_db[user_id]
    update_data = user_data.model_dump(exclude_unset=True)
    current_user.update(update_data)
    return current_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del users_db[user_id]
    return None