from fastapi import APIRouter, HTTPException
from app.models.movie import MovieName
from app.services.subtitle_service import get_movie_summary

router = APIRouter()

@router.post('/summarize')
async def summarize_movie_endpoint(movie: MovieName):
    try:
        moviename = movie.moviename
        print(f"Processing movie: {moviename}")
        summary = await get_movie_summary(moviename)
        return summary
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=f"File not found: {e.filename}")
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
