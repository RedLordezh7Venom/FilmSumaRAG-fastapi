from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import summary

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://film-suma-rag-frontend-inky.vercel.app/","https://filmsumarag-frontend.onrender.com/","https://filmsumarag-frontend.onrender.com/summary/","https://film-suma-rag-frontend-inky.vercel.app/summary/"],
    allow_credentials=True,
    allow_methods=["*"],  # Restrict to needed methods
    allow_headers=["*"]
)

app.include_router(summary.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
