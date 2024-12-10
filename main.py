from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
import json
from typing import List, Optional
import os

app = FastAPI(title="Movie API")

# Pydantic model for Movie
class Movie(BaseModel):
    id: int
    title: str
    release_date: date
    director: str

# Path to JSON file
JSON_FILE = "./data/movies.json"

# Initialize JSON file if it doesn't exist
def initialize_json():
    if not os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'w') as f:
            json.dump({"movies": []}, f)

# Helper function to read movies from JSON
def read_movies():
    with open(JSON_FILE, 'r') as f:
        return json.load(f)

# Helper function to write movies to JSON
def write_movies(data):
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f, default=str)

# Initialize JSON file
initialize_json()

@app.get("/movies", response_model=List[Movie])
async def get_movies():
    """Get all movies"""
    data = read_movies()
    return data["movies"]

@app.get("/movies/{movie_id}", response_model=Movie)
async def get_movie(movie_id: int):
    """Get a specific movie by ID"""
    data = read_movies()
    for movie in data["movies"]:
        if movie["id"] == movie_id:
            return movie
    raise HTTPException(status_code=404, detail="Movie not found")

@app.post("/movies", response_model=Movie)
async def create_movie(movie: Movie):
    """Create a new movie"""
    data = read_movies()
    
    # Check if movie ID already exists
    if any(m["id"] == movie.id for m in data["movies"]):
        raise HTTPException(status_code=400, detail="Movie ID already exists")
    
    data["movies"].append(movie.dict())
    write_movies(data)
    return movie

@app.put("/movies/{movie_id}", response_model=Movie)
async def update_movie(movie_id: int, movie: Movie):
    """Update an existing movie"""
    data = read_movies()
    
    for i, m in enumerate(data["movies"]):
        if m["id"] == movie_id:
            data["movies"][i] = movie.dict()
            write_movies(data)
            return movie
            
    raise HTTPException(status_code=404, detail="Movie not found")

@app.delete("/movies/{movie_id}")
async def delete_movie(movie_id: int):
    """Delete a movie"""
    data = read_movies()
    
    for i, m in enumerate(data["movies"]):
        if m["id"] == movie_id:
            del data["movies"][i]
            write_movies(data)
            return {"message": "Movie deleted"}
            
    raise HTTPException(status_code=404, detail="Movie not found")