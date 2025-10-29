import os
import magic
from PIL import Image
import aiofiles
from app.exceptions import FileValidationError

class FileValidator:
    SUPPORTED_FORMATS = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_TOTAL_FILES = 10
    MAX_TOTAL_SIZE = 50 * 1024 * 1024  # 50MB общий лимит
    
    @staticmethod
    async def validate_upload_file(file) -> dict:
        """Валидация одного загружаемого файла"""
        
        # Проверка размера файла
        if hasattr(file, 'size') and file.size > FileValidator.MAX_FILE_SIZE:
            raise FileValidationError(
                f"File '{file.filename}' too large. Maximum size is {FileValidator.MAX_FILE_SIZE // 1024 // 1024}MB",
                {
                    "max_size": FileValidator.MAX_FILE_SIZE, 
                    "actual_size": file.size,
                    "filename": file.filename
                }
            )
        
        # Проверка MIME типа
        mime_type = await FileValidator._get_mime_type(file)
        if mime_type not in FileValidator.SUPPORTED_FORMATS:
            raise FileValidationError(
                f"Unsupported file format for '{file.filename}': {mime_type}. Supported: {', '.join(FileValidator.SUPPORTED_FORMATS)}",
                {
                    "supported_formats": FileValidator.SUPPORTED_FORMATS, 
                    "actual_format": mime_type,
                    "filename": file.filename
                }
            )
        
        # Проверка содержимого через PIL
        try:
            await FileValidator._validate_image_content(file)
        except Exception as e:
            raise FileValidationError(
                f"Invalid image content for '{file.filename}': {str(e)}",
                {
                    "reason": "corrupted_or_invalid_image",
                    "filename": file.filename
                }
            )
        
        return {
            "mime_type": mime_type,
            "size": getattr(file, 'size', 0),
            "filename": file.filename,
            "is_valid": True
        }
    
    @staticmethod
    async def validate_multiple_files(files: list) -> dict:
        """Валидация множественных файлов"""
        
        # Проверка количества файлов
        if len(files) > FileValidator.MAX_TOTAL_FILES:
            raise FileValidationError(
                f"Too many files. Maximum {FileValidator.MAX_TOTAL_FILES} images allowed",
                {
                    "max_files": FileValidator.MAX_TOTAL_FILES,
                    "actual_files": len(files)
                }
            )
        
        if len(files) == 0:
            raise FileValidationError(
                "No files provided",
                {"min_files": 1, "actual_files": 0}
            )
        
        # Проверка общего размера
        total_size = sum(getattr(file, 'size', 0) for file in files)
        if total_size > FileValidator.MAX_TOTAL_SIZE:
            raise FileValidationError(
                f"Total files size too large. Maximum {FileValidator.MAX_TOTAL_SIZE // 1024 // 1024}MB allowed",
                {
                    "max_total_size": FileValidator.MAX_TOTAL_SIZE,
                    "actual_total_size": total_size
                }
            )
        
        # Валидация каждого файла
        validation_results = []
        for file in files:
            try:
                result = await FileValidator.validate_upload_file(file)
                validation_results.append(result)
            except FileValidationError as e:
                # Перебрасываем ошибку с информацией о файле
                raise FileValidationError(
                    f"Validation failed for file '{file.filename}': {e.message}",
                    {**e.details, "filename": file.filename}
                )
        
        return {
            "total_files": len(files),
            "total_size": total_size,
            "files": validation_results,
            "all_valid": True
        }
    
    @staticmethod
    async def _get_mime_type(file) -> str:
        """Определение MIME типа файла"""
        # Сначала используем content_type из UploadFile
        if hasattr(file, 'content_type') and file.content_type:
            return file.content_type.lower()
        
        # Если нет, определяем по содержимому
        content = await file.read(1024)  # Читаем первые 1024 байта
        await file.seek(0)  # Возвращаем указатель на начало
        
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(content).lower()
        return mime_type
    
    @staticmethod
    async def _validate_image_content(file):
        """Проверка валидности изображения через PIL"""
        temp_path = None
        try:
            # Создаем временный файл
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.img') as temp_file:
                temp_path = temp_file.name
            
            # Сохраняем содержимое файла
            async with aiofiles.open(temp_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            await file.seek(0)  # Возвращаем указатель
            
            # Пробуем открыть через PIL
            with Image.open(temp_path) as img:
                img.verify()  # Проверяем целостность файла
                
                # Дополнительная проверка - пробуем конвертировать
                img = Image.open(temp_path)  # Открываем заново после verify
                img.thumbnail((100, 100))  # Пробуем изменить размер
                
        except Exception as e:
            raise FileValidationError(f"Invalid image content: {str(e)}")
        finally:
            # Удаляем временный файл
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)