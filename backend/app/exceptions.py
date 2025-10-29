from fastapi import HTTPException
from fastapi.responses import JSONResponse
import time

class BoardOCRException(Exception):
    """Базовое исключение для приложения"""
    def __init__(self, error_code: str, message: str, status_code: int = 400):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class FileValidationError(BoardOCRException):
    """Ошибка валидации файла"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            error_code="FILE_VALIDATION_ERROR",
            message=message,
            status_code=400
        )
        self.details = details or {}

class TooManyFilesError(BoardOCRException):
    """Слишком много файлов"""
    def __init__(self, message: str, max_files: int, actual_files: int):
        super().__init__(
            error_code="TOO_MANY_FILES",
            message=message,
            status_code=400
        )
        self.details = {
            "max_files": max_files,
            "actual_files": actual_files
        }

class MLServiceError(BoardOCRException):
    """Ошибка ML-сервиса"""
    def __init__(self, message: str, ml_status_code: int = None):
        super().__init__(
            error_code="ML_SERVICE_ERROR",
            message=message,
            status_code=502
        )
        self.ml_status_code = ml_status_code

class PDFGenerationError(BoardOCRException):
    """Ошибка генерации PDF"""
    def __init__(self, message: str):
        super().__init__(
            error_code="PDF_GENERATION_ERROR",
            message=message,
            status_code=500
        )

async def custom_exception_handler(request, exc: BoardOCRException):
    """Глобальный обработчик исключений"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": getattr(exc, 'details', {}),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "path": request.url.path
        }
    )

def setup_exception_handlers(app):
    """Настройка обработчиков исключений"""
    app.add_exception_handler(BoardOCRException, custom_exception_handler)
    app.add_exception_handler(FileValidationError, custom_exception_handler)
    app.add_exception_handler(TooManyFilesError, custom_exception_handler)