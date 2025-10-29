from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import time
import logging
import asyncio
import aiofiles
from typing import List, Dict, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Board OCR Backend", 
    version="1.0.0",
    description="Backend for converting board notes to digital format with support for multiple images"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем директории
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

@app.get("/")
async def root():
    return {
        "message": "Board OCR Backend API", 
        "status": "running", 
        "version": "1.0.0",
        "features": {
            "max_files": 10,
            "max_file_size": "10MB",
            "supported_formats": ["JPEG", "PNG", "WebP"]
        }
    }

@app.post("/api/upload-images")
async def upload_multiple_images(
    files: List[UploadFile] = File(..., description="Up to 10 images of board notes"),
):
    """
    Эндпоинт для загрузки до 10 изображений доски
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        logger.info(f"Processing multiple images upload request: {request_id}, files: {len(files)}")
        
        # Проверка количества файлов
        if len(files) > 10:
            raise HTTPException(status_code=400, detail="Too many files. Maximum 10 images allowed")
        
        if len(files) == 0:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Сохраняем файлы
        saved_files = []
        
        for i, file in enumerate(files):
            # Проверка типа файла
            if not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not an image")
            
            # Сохраняем файл
            file_extension = os.path.splitext(file.filename)[1] or '.jpg'
            file_id = f"{request_id}_{i}"
            filename = f"{file_id}{file_extension}"
            file_path = os.path.join("uploads", filename)
            
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)
            
            saved_files.append({
                "file_id": file_id,
                "file_path": file_path,
                "filename": file.filename,
                "original_name": file.filename
            })
        
        # Обработка изображений
        processing_results = await process_multiple_images_parallel(saved_files, request_id)
        
        # Статистика обработки
        successful = sum(1 for r in processing_results if r["status"] == "success")
        failed = len(processing_results) - successful
        
        processing_time = time.time() - start_time
        
        return {
            "request_id": request_id,
            "status": "success" if successful > 0 else "error",
            "processed_images": processing_results,
            "total_images": len(files),
            "successful_processing": successful,
            "failed_processing": failed,
            "message": f"Processed {successful}/{len(files)} images successfully",
            "processing_time": round(processing_time, 2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_multiple_images: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during images processing")

@app.post("/api/generate-pdf")
async def generate_pdf(request_data: dict):
    """
    Эндпоинт для генерации PDF из нескольких обработанных изображений
    """
    try:
        request_id = request_data.get("request_id", str(uuid.uuid4()))
        images_data = request_data.get("images_data", [])
        title = request_data.get("title", "Board Notes")
        
        logger.info(f"Generating PDF for request: {request_id} with {len(images_data)} images")
        
        # Фильтруем только успешно обработанные изображения
        successful_images = [
            img for img in images_data 
            if img.get('status') == 'success' and img.get('extracted_text')
        ]
        
        if not successful_images:
            raise HTTPException(status_code=400, detail="No successfully processed images with text content available")
        
        # Генерируем PDF
        pdf_filename = f"{request_id}.pdf"
        pdf_path = os.path.join("outputs", pdf_filename)
        
        # Импортируем здесь чтобы избежать циклических импортов
        from app.utils.pdf_generator import create_pdf_from_multiple_images
        
        success = create_pdf_from_multiple_images(
            successful_images, 
            pdf_path,
            title
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to generate PDF file from images")
        
        # Получаем информацию о файле
        file_size = os.path.getsize(pdf_path)
        
        return {
            "request_id": request_id,
            "status": "success",
            "pdf_url": f"/api/download-pdf/{pdf_filename}",
            "file_size": file_size,
            "total_pages": len(successful_images),
            "message": f"PDF generated successfully from {len(successful_images)} images"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_pdf: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@app.get("/api/download-pdf/{filename}")
async def download_pdf(filename: str):
    """
    Эндпоинт для скачивания PDF
    """
    try:
        # Защита от path traversal атак
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        file_path = os.path.join("outputs", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        return FileResponse(
            path=file_path,
            filename=f"board_notes_{filename}",
            media_type='application/pdf'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Error downloading file")

async def process_multiple_images_parallel(saved_files: List[Dict], request_id: str) -> List[Dict]:
    """
    Параллельная обработка нескольких изображений
    """
    tasks = []
    for file_info in saved_files:
        task = process_single_image(file_info, request_id)
        tasks.append(task)
    
    # Запускаем все задачи параллельно
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Обрабатываем результаты
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            # Ошибка обработки одного изображения
            processed_results.append({
                "image_id": saved_files[i]["file_id"],
                "filename": saved_files[i]["original_name"],
                "status": "error",
                "error_message": str(result),
                "processing_time": 0
            })
            logger.error(f"Error processing image {saved_files[i]['filename']}: {str(result)}")
        else:
            processed_results.append(result)
    
    return processed_results

async def process_single_image(file_info: Dict, request_id: str) -> Dict:
    """
    Обработка одного изображения
    """
    start_time = time.time()
    
    try:
        # Имитация вызова ML-сервиса для OCR
        extracted_data = await call_ml_service_safe(file_info["file_path"], file_info["file_id"])
        
        processing_time = time.time() - start_time
        
        return {
            "image_id": file_info["file_id"],
            "filename": file_info["original_name"],
            "status": "success",
            "extracted_text": extracted_data["text"],
            "infographics": extracted_data["infographics"],
            "processing_time": round(processing_time, 2)
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        return {
            "image_id": file_info["file_id"],
            "filename": file_info["original_name"],
            "status": "error",
            "error_message": str(e),
            "processing_time": round(processing_time, 2)
        }

async def call_ml_service_safe(image_path: str, image_id: str) -> Dict[str, Any]:
    """
    Безопасный вызов ML-сервиса для OCR (заглушка)
    """
    try:
        # Имитация обработки ML-модулем
        await asyncio.sleep(1)  # Имитация времени обработки
        
        # Генерируем уникальный текст для каждого изображения
        base_text = f"""РАСПОЗНАННЫЙ ТЕКСТ С ДОСКИ (Изображение: {image_id})

Тема: Разработка OCR-системы с поддержкой множественных изображений
• Загрузка {image_id} ✓
• Валидация файлов ✓  
• Параллельная обработка ✓
• Генерация комбинированного PDF ✓

Особенности системы:
- Поддержка до 10 изображений
- Параллельная обработка
- Детальная статистика
- Обработка ошибок на уровне отдельных файлов

Это текст из изображения {image_id}"""
        
        return {
            "text": base_text,
            "infographics": [
                {"type": "diagram", "data": f"diagram_data_{image_id}"},
                {"type": "chart", "data": f"chart_data_{image_id}"}
            ]
        }
        
    except Exception as e:
        logger.error(f"ML service error for {image_id}: {str(e)}")
        raise Exception(f"OCR processing failed: {str(e)}")

# Обработчик для общих исключений
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Обработчик для непредвиденных исключений"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "path": request.url.path
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)