from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from typing import List

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

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
    
    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(back_populates="customer" ,cascade="all, delete")
    
class Mechanic(Base):
    __tablename__ = "mechanics"
    
    id : Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(100),unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(100), nullable=False)
    salary: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    
    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(secondary=service_mechanic,back_populates="mechanics")

class ServiceTicket(Base):
    __tablename__ = "service_tickets"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(db.String(255), nullable=False)
    service_date: Mapped[date] = mapped_column(nullable=False)
    service_desc: Mapped[str] = mapped_column(db.String(255), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customers.id"), nullable=False)
    
    customer: Mapped["Customer"] = db.relationship(back_populates="service_tickets")
    mechanics: Mapped[List["Mechanic"]] = db.relationship(secondary=service_mechanic, back_populates="service_tickets")
    