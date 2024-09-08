from datetime import datetime
import uuid
from assessment_app.repository.database import Base, engine


from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID


class Posts(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String)
    description = Column(String)


class UserCredentials(Base):
    
    __tablename__ = "user_credentials"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String)
    password_hash = Column(String)
    random_salt = Column(String)


class TradeData(Base):

    __tablename__ = "trade_data"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    symbol = Column(String)
    date = Column(DateTime)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adj_close = Column(Float)
    volume = Column(Float)



Base.metadata.create_all(engine)

