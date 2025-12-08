from sqlalchemy import Boolean, Column, Integer, String
from database import Base

class flights(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    airline = Column(String(50))
    flight_number = Column(String(10), unique=True, index=True)
    departure_city = Column(String(50))
    departure_time = Column(String(50))
    stops = Column(Integer)
    arrival_time = Column(String(50))
    arrival_city = Column(String(50))
    travel_class = Column(String(20))
    duration = Column(String(20))
    days_left = Column(Integer)
    price = Column(Integer)


"""class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    
class post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50))
    content = Column(String(100))
    user_id = Column(Integer)"""