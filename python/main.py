import os
import logging
import pathlib
import json

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "image"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...)):
    logger.info(f"Receive item: {name}")

    # json format to be written
    items_list = {"items" : []}

    # if item.json exsits, load the data first
    if os.path.isfile('items.json'):
        with open('items.json') as item_json_file:
            items_list = json.load(item_json_file)

    # add new item
    new_item = {"name": name, "category": category}
    items_list["items"].append(new_item)

    # Writing to item.json
    with open("items.json", "w") as item_json_file:
        json.dump(items_list, item_json_file, indent = 4)

    return {"message": f"item received: {name}"}

@app.get("/items")
def get_items():
    items_list = {"items" : []}

    # if item.json exsits, load the data
    if os.path.isfile('items.json') :
        with open('items.json') as item_json_file:
            items_list = json.load(item_json_file)

    return items_list

@app.get("/image/{items_image}")
async def get_image(items_image):
    # Create image path
    image = images / items_image

    if not items_image.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)
