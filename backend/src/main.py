from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.database import database, init_db
from src.features.ivr.router import router as ivr_router
from src.features.dashboard.router import router as dashboard_router

app = FastAPI(title="RojinMatch API")

# CORS for frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()
    init_db()  # Create tables if not exist
    print("Database connected and initialized.")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.include_router(ivr_router, prefix="/api/ivr", tags=["IVR"])
app.include_router(dashboard_router, tags=["Dashboard"])

@app.get("/")
def read_root():
    return {"message": "RojinMatch Backend Running"}
