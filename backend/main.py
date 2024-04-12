from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import motor.motor_asyncio 
import os

app = FastAPI()

# Connect to MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get('MONGO_URI', 'mongodb://localhost:27017'))
db = client['bookdb']
collection = db['items']

# Example data
#fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

class Item(BaseModel):
    item_name: str

# CRUD operations
@app.get("/items/", response_model=List[Item])
async def read_items():
    items = await collection.find().to_list(length=None)
    return items

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    print(item_id)
    item = await collection.find_one({"_id": item_id})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items/")
async def create_item(item: Item):
    await collection.insert_one(item.dict())
    return {"message": "Item created successfully"}

@app.put("/items/{item_name}")
async def update_item(item_name: str, item: Item):
    await collection.replace_one({"item_name": item_name}, item.dict())
    return {"message": f"Item '{item_name}' updated successfully"}

@app.delete("/items/{item_name}")
async def delete_item(item_name: str):
    await collection.delete_one({"item_name": item_name})
    return {"message": f"Item '{item_name}' deleted successfully"}

# Adding Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return JSONResponse(content=app.openapi_html)

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return JSONResponse(content=app.openapi())

# Serve React.js frontend
app.mount("/", StaticFiles(directory="static", html=True))
