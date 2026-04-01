# 🍽️ FoodHub - Unified Food Ordering System

FoodHub is a complete, real-time food ordering and restaurant management platform. It features a modern, responsive interface for customers, waitstaff, kitchen personnel, and administrators.

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Node.js 18+

### 2. Backend Setup
```bash
cd backend
# Database is configured to run in-memory for zero-setup testing
python -m uvicorn app.main:app --reload
```
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- **Application URL**: [http://localhost:5173](http://localhost:5173)

---

## 🔑 Default Administrator Credentials
Since the system currently uses an **in-memory SQLite database**, a default administrator is seeded automatically on startup:
- **Email:** `admin@foodhub.com`
- **Password:** `admin123`

---

## 🌟 Key Features

### 🛒 Customer
- **Live Menu**: Browse categorized dishes with real-time availability.
- **Persistent Cart**: Manage items and notes before placing an order.
- **Live Tracking**: Monitor order status (`Placed` ➔ `Preparing` ➔ `Cooking` ➔ `Ready to Serve`) via WebSockets.

### 🍱 Waitstaff
- **Service Dashboard**: Instantly see orders that are ready to be delivered to tables.
- **Order Management**: Mark items as served to complete the order lifecycle.

### 🍳 Kitchen
- **Cooking Workflow**: Manage the active queue of orders and update statuses as they progress.
- **Real-time Notifications**: Receive new orders immediately without refreshing.

### 📊 Administrator
- **Menu Control**: Full CRUD operations for menu items, prices, and availability.
- **Analytics Dashboard**: View revenue trends, order volumes, and popular dishes.
- **User Management**: Overview of all registered staff and customers.

---

## 🛠️ Technology Stack
- **Backend**: FastAPI, SQLAlchemy 2.0, Pydantic, JWT Auth, WebSockets.
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide React (Icons).
- **Database**: SQLite (Configured for In-Memory local development).

## 📁 Project Structure
```text
food-ordering-system/
├── backend/            # FastAPI Application
│   ├── app/
│   │   ├── models/     # SQLAlchemy Database Models
│   │   ├── routers/    # API Endpoints
│   │   ├── schemas/    # Pydantic Data Models
│   │   └── main.py     # Entry Point
│   └── requirements.txt
├── frontend/           # React + Vite Application
│   ├── src/
│   │   ├── pages/      # Role-specific Dashboards
│   │   ├── components/ # Reusable UI Components
│   │   └── context/    # Auth & State Management
│   └── package.json
└── .gitignore          # Unified Git Ignore Rules
```
