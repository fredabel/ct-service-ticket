from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date, datetime, timezone
from typing import List

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
# local_dt = utc_dt.astimezone() 
# print("Local time:", local_dt)

service_mechanic = db.Table(
    "service_mechanic",
    Base.metadata,
    db.Column("ticket_id",db.ForeignKey("service_tickets.id")),
    db.Column("mechanic_id",db.ForeignKey("mechanics.id"))
)

class Customer(Base):
    __tablename__ = "customers"
    id : Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(100),unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(100), nullable=False)
    address: Mapped[str] = mapped_column(db.String(255), nullable=True)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    image: Mapped[str] = mapped_column(db.String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(back_populates="customer", cascade="all, delete")
    
class Mechanic(Base):
    __tablename__ = "mechanics"
    
    id : Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(100),unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(100), nullable=False)
    address: Mapped[str] = mapped_column(db.String(255), nullable=True)
    salary: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    image: Mapped[str] = mapped_column(db.String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(secondary=service_mechanic,back_populates="mechanics")

class Category(db.Model):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    description: Mapped[str] = mapped_column(db.String(255), nullable=False)
    image: Mapped[str] = mapped_column(db.String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    parts: Mapped[List["PartDescription"]] = db.relationship(back_populates="category")
    
class PartDescription(Base):
    __tablename__ = "part_descriptions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    brand: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    image: Mapped[str] = mapped_column(db.String(255), nullable=True)
    category_id: Mapped[int] = mapped_column(db.ForeignKey("categories.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    serial_items : Mapped[List["SerializedPart"]] = db.relationship(back_populates="description")
    category: Mapped["Category"] = db.relationship(back_populates="parts")

class SerializedPart(Base):
    __tablename__ = "serialized_parts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    desc_id: Mapped[int] = mapped_column(db.ForeignKey('part_descriptions.id'), nullable=False)
    ticket_id: Mapped[int] = mapped_column(db.ForeignKey('service_tickets.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    description: Mapped["PartDescription"] = db.relationship(back_populates="serial_items")
    ticket: Mapped["ServiceTicket"] = db.relationship(back_populates="ticket_items")
    
class TicketStatus(db.Model):
    __tablename__ = 'ticket_status'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    description: Mapped[str] = mapped_column(db.String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    service_tickets : Mapped[List["ServiceTicket"]] = db.relationship(back_populates="status")
     
class Priority(db.Model):
    __tablename__ = 'priorities'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    description: Mapped[str] = mapped_column(db.String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    service_tickets : Mapped[List["ServiceTicket"]] = db.relationship(back_populates="priority") 
    
class ServiceTicket(Base):
    __tablename__ = "service_tickets"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customers.id"), nullable=False)
    vin: Mapped[str] = mapped_column(db.String(255), nullable=False)
    status_id: Mapped[int] = mapped_column(db.ForeignKey("ticket_status.id"), default=1, nullable=False)
    service_date: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    completion_date: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    service_desc: Mapped[str] = mapped_column(db.String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    estimated_cost: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=True) 
    actual_cost: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=True) 
    priority_id: Mapped[int] = mapped_column(db.ForeignKey("priorities.id"), default=1, nullable=False)
    
    
    customer: Mapped["Customer"] = db.relationship(back_populates="service_tickets")
    status: Mapped["TicketStatus"] = db.relationship(back_populates="service_tickets")
    priority: Mapped["Priority"] = db.relationship(back_populates="service_tickets")
    mechanics: Mapped[List["Mechanic"]] = db.relationship(secondary=service_mechanic, back_populates="service_tickets")
    ticket_items: Mapped[List["SerializedPart"]] = db.relationship(back_populates="ticket")