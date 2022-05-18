import os
import logging
import pathlib
import json
import sqlite3
import hashlib

from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# dbname = "../db/mercari.sqlite3"

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "image"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.post("/files/")
async def create_file(file: bytes = File()):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}

# Hash the image using sha256
def hash_image(image):
    with open(image, 'rb') as f: #バイナリモードとして画像ファイルを読み込む
        f.seek(0)
        image_hash = hashlib.sha256(f.read()).hexdigest()
        return (f'{image_hash}.jpg')

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.get("/search")
def search_item(keyword: str):
    # Establish connection and create a cursor
    conn = sqlite3.connect('../db/mercari.sqlite3')
    cur = conn.cursor()

    # select matching items
    cur.execute("SELECT * from items WHERE name LIKE (?)", (f"%{keyword}%", ))

    stored_items = cur.fetchall()
    items_list = {"items": [{"id": id, "name": name, "category": category, "image": image} for (id, name, category, image) in stored_items] }

    # Commit to the database and change will be reflected
    conn.close()

    return items_list


@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...), image: str = File()):
    logger.info(f"Receive item: {name}, {category}, {image}")

    # Establish a connection and create a cursor
    conn = sqlite3.connect('../db/mercari.sqlite3')
    cur = conn.cursor()

    # Insert name, category, and image
    cur.execute("INSERT INTO items (name, category, image) VALUES (?,?,?)", (name, category, hash_image(image)))

    # Commit to the database and change will be reflected
    conn.commit()
    conn.close()

    return {"message": f"item received: {name}"}

@app.get("/items")
def get_items():
    # Establish connection and create a cursor
    conn = sqlite3.connect('../db/mercari.sqlite3')
    cur = conn.cursor()

    # Get all items
    cur.execute("SELECT * FROM items")
    stored_items = cur.fetchall()
    items_list = {"items": stored_items}

    # Commit to the database and change will be reflected
    conn.commit()
    conn.close()

    return items_list

@app.get("/items/{item_id}")
def get_item(item_id=int):

    # Establish connection and create a cursor
    conn = sqlite3.connect('../db/mercari.sqlite3')
    cur = conn.cursor()

    cur.execute("SELECT * FROM items WHERE id IS " + item_id)
    items_list = {"items": [{"id": id, "name": name, "category": category, "image": image} for (id, name, category, image) in cur] }

    #close the database
    conn.close()

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
