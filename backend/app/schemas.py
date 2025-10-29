from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from enum import Enum
import re

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"

class MultiImageOCRRequest(BaseModel):
    request_id: Optional[str] = Field(None, description="Optional request ID")
    enhance_quality: bool = Field(False, description="Apply quality enhancement")
    
    @validator('request_id')
    def validate_request_id(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Request ID can only contain letters, numbers, underscores and hyphens')
        return v

class MultiImageOCRResponse(BaseModel):
    request_id: str
    status: ProcessingStatus
    processed_images: List[Dict[str, Any]]
    total_images: int
    successful_processing: int
    failed_processing: int
    message: Optional[str] = None
    processing_time: Optional[float] = None

class ImageProcessingResult(BaseModel):
    image_id: str
    filename: str
    status: ProcessingStatus
    extracted_text: Optional[str] = None
    infographics: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None

class PDFRequest(BaseModel):
    request_id: str = Field(..., description="Request ID from OCR processing")
    images_data: List[Dict[str, Any]] = Field(..., description="Processed images data")
    title: Optional[str] = Field("Board Notes", description="PDF title")
    
    @validator('images_data')
    def validate_images_data(cls, v):
        if not v:
            raise ValueError('At least one processed image required')
        if len(v) > 10:
            raise ValueError('Maximum 10 images allowed')
        return v

class PDFResponse(BaseModel):
    request_id: str
    status: ProcessingStatus
    pdf_url: str
    file_size: Optional[int] = None
    total_pages: Optional[int] = None
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str