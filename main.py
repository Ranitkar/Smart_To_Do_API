from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# --- CONFIGURATION ---
# In a real project, use a .env file for these values!
MONGO_URI = "mongodb+srv://Ranit:r123456@cluster0.yy3u0lg.mongodb.net/Smart_todo_api?retryWrites=true&w=majority&appName=Cluster0"  # REPLACE THIS
SECRET_KEY = "my_super_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="Smart ToDo API")

# --- DATABASE SETUP ---
client = AsyncIOMotorClient(MONGO_URI)
db = client.todo_db
users_collection = db.users
tasks_collection = db.tasks

# --- SECURITY & AUTH UTILS ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await users_collection.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user

# --- MODELS (Pydantic) ---

# Helper to handle MongoDB ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# User Models
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    id: Optional[str] = Field(alias="_id")

# Task Models
class TaskModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    title: str
    description: Optional[str] = None
    completed: bool = False
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TaskUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    completed: Optional[bool]

# --- ENDPOINTS ---

# 1. REGISTER
@app.post("/register", status_code=201)
async def register(user: UserCreate):
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = get_password_hash(user.password)
    user_dict = {"username": user.username, "password": hashed_password}
    await users_collection.insert_one(user_dict)
    return {"message": "User created successfully"}

# 2. LOGIN (Returns JWT)
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# 3. CREATE TASK (POST)
@app.post("/tasks", response_model=TaskModel)
async def create_task(task: TaskCreate, current_user: dict = Depends(get_current_user)):
    task_dict = task.dict()
    task_dict["owner_id"] = current_user["_id"] # Link task to user
    new_task = await tasks_collection.insert_one(task_dict)
    created_task = await tasks_collection.find_one({"_id": new_task.inserted_id})
    
    # Map _id to id for response
    created_task["id"] = str(created_task["_id"])
    return created_task

# 4. GET ALL TASKS (GET)
@app.get("/tasks", response_model=List[TaskModel])
async def get_tasks(current_user: dict = Depends(get_current_user)):
    tasks = []
    cursor = tasks_collection.find({"owner_id": current_user["_id"]})
    async for document in cursor:
        document["id"] = str(document["_id"])
        tasks.append(document)
    return tasks

# 5. UPDATE TASK (PUT)
@app.put("/tasks/{id}", response_model=TaskModel)
async def update_task(id: str, task: TaskUpdate, current_user: dict = Depends(get_current_user)):
    # Create update dictionary, removing None values
    update_data = {k: v for k, v in task.dict().items() if v is not None}
    
    if len(update_data) >= 1:
        update_result = await tasks_collection.update_one(
            {"_id": ObjectId(id), "owner_id": current_user["_id"]}, 
            {"$set": update_data}
        )
        if update_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Task not found or permission denied")

    if (existing_task := await tasks_collection.find_one({"_id": ObjectId(id)})) is not None:
        existing_task["id"] = str(existing_task["_id"])
        return existing_task

    raise HTTPException(status_code=404, detail="Task not found")

# 6. DELETE TASK (DELETE)
@app.delete("/tasks/{id}")
async def delete_task(id: str, current_user: dict = Depends(get_current_user)):
    delete_result = await tasks_collection.delete_one({"_id": ObjectId(id), "owner_id": current_user["_id"]})
    
    if delete_result.deleted_count == 1:
        return {"message": "Task deleted"}
    
    raise HTTPException(status_code=404, detail="Task not found or permission denied")