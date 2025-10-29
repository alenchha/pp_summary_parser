from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship  # ✅ ДОБАВЬ relationship!
from sqlalchemy.sql import func
import datetime
import uuid

# Базовый класс для моделей
Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class ProcessingRequest(Base):
    """
    Модель для хранения информации о запросах на обработку
    """
    __tablename__ = "processing_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(36), unique=True, index=True, default=generate_uuid)
    user_id = Column(String(100), index=True, nullable=True)
    status = Column(String(20), default="pending")
    total_images = Column(Integer, default=0)
    successful_processing = Column(Integer, default=0)
    failed_processing = Column(Integer, default=0)
    processing_time = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    error_message = Column(Text, nullable=True)
    
    # Связь с изображениями
    images = relationship("ProcessedImage", back_populates="request")  # ✅ Теперь работает!

class ProcessedImage(Base):
    """
    Модель для хранения информации об обработанных изображениях
    """
    __tablename__ = "processed_images"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(String(100), unique=True, index=True)
    filename = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    # Результаты OCR
    extracted_text = Column(Text, nullable=True)
    infographics = Column(JSON, nullable=True)
    
    # Статус обработки
    status = Column(String(20), default="pending")
    processing_time = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Метрики качества
    confidence_score = Column(Float, nullable=True)
    text_length = Column(Integer, default=0)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Внешний ключ
    request_id = Column(Integer, ForeignKey("processing_requests.id"))
    request = relationship("ProcessingRequest", back_populates="images")

class GeneratedPDF(Base):
    """
    Модель для хранения информации о сгенерированных PDF файлах
    """
    __tablename__ = "generated_pdfs"
    
    id = Column(Integer, primary_key=True, index=True)
    pdf_id = Column(String(36), unique=True, index=True, default=generate_uuid)
    filename = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)
    total_pages = Column(Integer, default=1)
    title = Column(String(255), default="Board Notes")
    
    # Связь с запросом
    request_id = Column(String(36))  # Упростим без ForeignKey для начала
    
    # Информация о содержимом
    total_images = Column(Integer, default=0)
    total_text_length = Column(Integer, default=0)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    downloaded_count = Column(Integer, default=0)
    
    # Метаданные
    pdf_metadata = Column(JSON, nullable=True)

# Настройка подключения к БД
SQLALCHEMY_DATABASE_URL = "sqlite:///./board_ocr.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency для получения сессии БД
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Создание таблиц в БД
    """
    Base.pdf_metadata.create_all(bind=engine)

def init_db():
    """
    Инициализация базы данных
    """
    create_tables()
    print("✅ Database tables created successfully")