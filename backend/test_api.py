#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://127.0.0.1:8000"  # Используем IP вместо localhost

def print_response(response, title):
    print(f"\n{'='*50}")
    print(f"📋 {title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(f"Response Text: {response.text}")
    print(f"{'='*50}")

def test_root():
    print("🧪 Тестирование корневого эндпоинта...")
    response = requests.get(f"{BASE_URL}/")
    print_response(response, "Root Endpoint")
    return response.status_code == 200

def test_generate_pdf():
    print("🧪 Тестирование генерации PDF...")
    
    test_data = {
        "request_id": "test_123",
        "images_data": [
            {
                "image_id": "img_1",
                "filename": "test1.jpg",
                "status": "success",
                "extracted_text": "Это тестовый текст с доски\n• Математика: 2+2=4\n• Физика: F=ma\n• Химия: H2O",
                "infographics": [{"type": "diagram", "data": "test_data"}],
                "processing_time": 1.5
            }
        ],
        "title": "Тестовые заметки с доски"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/generate-pdf",
        json=test_data,
        timeout=30
    )
    
    print_response(response, "Generate PDF")
    
    if response.status_code == 200:
        data = response.json()
        print(f"📄 PDF создан: {data.get('pdf_url')}")
        return True
    return False

def test_download_pdf():
    print("🧪 Тестирование скачивания PDF...")
    
    # Сначала создаем PDF
    test_data = {
        "request_id": "download_test",
        "images_data": [
            {
                "image_id": "img_1", 
                "filename": "test.jpg",
                "status": "success",
                "extracted_text": "Текст для тестового PDF",
                "infographics": []
            }
        ]
    }
    
    create_response = requests.post(f"{BASE_URL}/api/generate-pdf", json=test_data)
    
    if create_response.status_code == 200:
        pdf_url = create_response.json().get('pdf_url')
        filename = pdf_url.split('/')[-1]
        
        # Скачиваем PDF
        download_response = requests.get(f"{BASE_URL}{pdf_url}")
        print_response(download_response, "Download PDF")
        
        if download_response.status_code == 200:
            # Сохраняем файл
            with open(f"test_output_{filename}", 'wb') as f:
                f.write(download_response.content)
            print(f"✅ PDF сохранен как: test_output_{filename}")
            return True
    
    return False

def main():
    print("🚀 Запуск финальных тестов API")
    print("=" * 50)
    
    tests = [
        ("Корневой эндпоинт", test_root),
        ("Генерация PDF", test_generate_pdf),
        ("Скачивание PDF", test_download_pdf)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n🔹 Тест: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name} - ПРОЙДЕН")
                passed += 1
            else:
                print(f"❌ {test_name} - НЕ ПРОЙДЕН")
        except Exception as e:
            print(f"❌ {test_name} - ОШИБКА: {e}")
    
    print(f"\n📊 Результаты: {passed}/{len(tests)} тестов пройдено")
    
    if passed == len(tests):
        print("🎉 Все тесты пройдены! API работает корректно.")
        print("📚 Документация: http://127.0.0.1:8000/docs")
    else:
        print("⚠️ Некоторые тесты не пройдены")

if __name__ == "__main__":
    main()