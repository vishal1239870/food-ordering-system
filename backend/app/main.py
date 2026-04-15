from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from .config import settings
from .database import get_db, db
from .routers import auth, menu, cart, orders, kitchen, waiter, admin
from .websockets.manager import manager
from .dependencies.auth import decode_token, get_password_hash
from .models.user import User
from .models.menu import MenuItem
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Online Food Ordering System API (MongoDB Edition)",
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
        "message": "Welcome to FoodHub API (MongoDB)",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "mongodb"}

# WebSocket endpoint for real-time updates
@app.websocket("/ws/{token}")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str
):
    """WebSocket endpoint for real-time order updates"""
    try:
        # Decode token and get user
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=1008)
            return
        
        from bson import ObjectId
        # Get user from MongoDB
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        except Exception:
            user_doc = None
            
        if not user_doc:
            # Try searching by string ID if needed
            user_doc = await db.users.find_one({"id": user_id})

        if not user_doc:
            await websocket.close(code=1008)
            return
        
        user_role = user_doc.get("role", "customer")
        
        # Connect based on role
        if user_role == "customer":
            await manager.connect(websocket, user_id=user_id)
        else:
            await manager.connect(websocket, user_id=user_id, role=user_role)
        
        try:
            # Keep connection alive and handle messages
            while True:
                data = await websocket.receive_text()
                # Echo back for ping/pong
                await websocket.send_json({"type": "pong", "message": "Connection alive"})
        
        except WebSocketDisconnect:
            if user_role == "customer":
                manager.disconnect(websocket, user_id=user_id)
            else:
                manager.disconnect(websocket, user_id=user_id, role=user_role)
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=1011)

# Startup event
@app.on_event("startup")
async def startup_event():
    print(f"{settings.APP_NAME} started successfully (MongoDB)")
    print(f"API Docs: http://localhost:8000/docs")

    # Seed default users
    try:
        users_to_seed = [
            {"name": "System Admin", "email": "admin@foodhub.com", "password": "admin123", "role": "admin"},
            {"name": "John Customer", "email": "john@example.com", "password": "admin123", "role": "customer"},
            {"name": "Jane Waiter", "email": "jane@foodhub.com", "password": "admin123", "role": "waiter"},
            {"name": "Mike Chef", "email": "mike@foodhub.com", "password": "admin123", "role": "kitchen"},
        ]

        for user_data in users_to_seed:
            try:
                existing_user = await db.users.find_one({"email": user_data["email"]})
                if not existing_user:
                    print(f"Seeding user: {user_data['email']} ({user_data['role']})")
                    hashed_password = get_password_hash(user_data["password"])
                    new_user = {
                        "name": user_data["name"],
                        "email": user_data["email"],
                        "password": hashed_password,
                        "role": user_data["role"],
                        "created_at": datetime.utcnow()
                    }
                    result = await db.users.insert_one(new_user)
                    
                    # Create cart for customer
                    if user_data["role"] == "customer":
                        await db.carts.insert_one({
                            "user_id": str(result.inserted_id),
                            "items": [],
                            "updated_at": datetime.utcnow()
                        })
                else:
                    # Update password to new scheme if it's currently md5 or broken
                    stored_pwd = existing_user.get("password", "")
                    if stored_pwd.startswith("$2") or not stored_pwd.startswith("$pbkdf2"):
                         print(f"Migrating password hash for: {user_data['email']}")
                         new_hashed = get_password_hash(user_data["password"])
                         await db.users.update_one(
                             {"_id": existing_user["_id"]},
                             {"$set": {"password": new_hashed}}
                         )
            except Exception as user_e:
                print(f"Error seeding user {user_data['email']}: {user_e}")

        # Seed default menu items
        try:
            existing_items = await db.menu_items.find_one({})
            if not existing_items:
                print("Seeding default menu items...")
                default_items = [
                    {
                        "name": "Classic Cheeseburger",
                        "description": "Juicy beef patty with cheddar cheese, lettuce, tomato, and our special sauce.",
                        "price": 9.99,
                        "category": "Burgers",
                        "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?q=80&w=500&auto=format&fit=crop"
                    },
                    {
                        "name": "Margherita Pizza",
                        "description": "Traditional wood-fired pizza with fresh mozzarella, tomatoes, and basil.",
                        "price": 14.50,
                        "category": "Pizza",
                        "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?q=80&w=500&auto=format&fit=crop"
                    },
                    {
                        "name": "Caesar Salad",
                        "description": "Crisp romaine lettuce, croutons, parmesan cheese, and Caesar dressing.",
                        "price": 8.99,
                        "category": "Salads",
                        "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?q=80&w=500&auto=format&fit=crop"
                    },
                    {
                        "name": "Creamy Pesto Pasta",
                        "description": "Penne pasta tossed in a rich, creamy basil pesto sauce with pine nuts.",
                        "price": 15.50,
                        "category": "Pasta",
                        "image_url": "https://images.unsplash.com/photo-1473093226795-af9932fe5856?q=80&w=500&auto=format&fit=crop"
                    },
                    {
                        "name": "Chocolate Lava Cake",
                        "description": "Warm chocolate cake with a gooey center, served with vanilla bean ice cream.",
                        "price": 7.50,
                        "category": "Desserts",
                        "image_url": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?q=80&w=500&auto=format&fit=crop"
                    }
                ]
                for item in default_items:
                    item["created_at"] = datetime.utcnow()
                    item["updated_at"] = datetime.utcnow()
                    item["available"] = True
                
                await db.menu_items.insert_many(default_items)
                print("Menu items seeded successfully")
        except Exception as menu_e:
            print(f"Error seeding products: {menu_e}")
            
    except Exception as e:
        print(f"Error during startup database operations: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down application...")

# Serving static files
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")

if os.path.exists(static_dir):
    # Mount assets folder if it exists
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Catch-all route to serve index.html for React SPA
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Let API and WebSocket paths be handled by routers
        if full_path.startswith("api") or full_path.startswith("ws"):
            return None
        
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Welcome to FoodHub API (MongoDB)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )