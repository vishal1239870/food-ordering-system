from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, DateTime, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base

class OrderStatus(str, enum.Enum):
    PLACED = "Placed"
    PREPARING = "Preparing"
    COOKING = "Cooking"
    READY_TO_SERVE = "Ready to Serve"
    SERVED = "Served"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    # FIX: Use native_enum=False
    status = Column(SQLEnum(OrderStatus, native_enum=False, values_callable=lambda x: [e.value for e in x]), default=OrderStatus.PLACED, index=True)
    payment_status = Column(SQLEnum(PaymentStatus, native_enum=False, values_callable=lambda x: [e.value for e in x]), default=PaymentStatus.PENDING)
    notes = Column(Text)
    table_number = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")