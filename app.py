from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import date
import json
from typing import List, Optional
import os
from math import ceil

app = FastAPI(title="Movie API")

# Pydantic models with validation
class Movie(BaseModel):
    id: int
    title: str
    release_date: date
    director: str

class PaginatedMovieResponse(BaseModel):
    total_items: int
    total_pages: int
    current_page: int
    items_per_page: int
    movies: List[Movie]

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

# Constants for pagination
MIN_PAGE_SIZE = 1
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 10

@app.get("/movies", response_model=PaginatedMovieResponse)
async def get_movies(

    items_per_page: int = Query(
        default=DEFAULT_PAGE_SIZE,
        ge=MIN_PAGE_SIZE,
        le=MAX_PAGE_SIZE,
        alias="size",
        description=f"Number of items per page (minimum: {MIN_PAGE_SIZE}, maximum: {MAX_PAGE_SIZE})"
    )
):
    """
    Get paginated list of movies.
    - page: Page number (starts from 1)
    - items_per_page: Number of items per page (default: 10, min: 1, max: 100)
    """
    data = read_movies()
    total_items = len(data["movies"])
    
    # Calculate total pages
    total_pages = ceil(total_items / items_per_page)
    
    # Validate page number against total pages
    if total_items > 0 and page > total_pages:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Page not found",
                "total_pages": total_pages,
                "current_page": page,
                "total_items": total_items
            }
        )
    
    # Calculate start and end indices
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    # Get paginated movies
    paginated_movies = data["movies"][start_idx:end_idx]
    
    # Return response with pagination metadata
    return {
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "items_per_page": items_per_page,
        "movies": paginated_movies
    }

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