from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db, engine, Base
from .routers import auth, menu, cart, orders, kitchen, waiter, admin
from .websockets.manager import manager
from .dependencies.auth import decode_token
from .models.user import User

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Online Food Ordering System API",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(kitchen.router)
app.include_router(waiter.router)
app.include_router(admin.router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to FoodHub API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# WebSocket endpoint for real-time updates
@app.websocket("/ws/{token}")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time order updates"""
    try:
        # Decode token and get user
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=1008)
            return
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await websocket.close(code=1008)
            return
        
        # Connect based on role
        if user.role == "customer":
            await manager.connect(websocket, user_id=user.id)
        else:
            await manager.connect(websocket, user_id=user.id, role=user.role)
        
        try:
            # Keep connection alive and handle messages
            while True:
                data = await websocket.receive_text()
                # Echo back for ping/pong
                await websocket.send_json({"type": "pong", "message": "Connection alive"})
        
        except WebSocketDisconnect:
            if user.role == "customer":
                manager.disconnect(websocket, user_id=user.id)
            else:
                manager.disconnect(websocket, user_id=user.id, role=user.role)
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=1011)

# Startup event
@app.on_event("startup")
async def startup_event():
    print(f"{settings.APP_NAME} started successfully")
    print(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'Not configured'}")
    print(f"API Docs: http://localhost:8000/docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down application...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )