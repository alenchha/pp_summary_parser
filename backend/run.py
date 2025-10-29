#!/usr/bin/env python3
"""
Скрипт для запуска Board OCR Backend
"""
import uvicorn
import os

def create_directories():
    """Создание необходимых директорий"""
    directories = ["uploads", "outputs"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Создана директория: {directory}")

def main():
    print("🚀 Запуск Board OCR Backend...")
    print("=" * 50)
    
    # Создание директорий
    create_directories()
    
    # Запуск сервера
    print("\n🌐 Сервер запускается...")
    print("📚 Документация API: http://localhost:8000/docs")
    print("🛑 Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()