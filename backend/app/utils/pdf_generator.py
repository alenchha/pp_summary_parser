from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
import os

def create_pdf_from_multiple_images(images_data: list, output_path: str, title: str = "Board Notes"):
    """
    Создает PDF файл из нескольких обработанных изображений
    """
    try:
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        subtitle_style = styles['Heading2']
        normal_style = styles['BodyText']
        
        story = []
        
        # Главный заголовок
        main_title = Paragraph(f"{title} - {len(images_data)} images", title_style)
        story.append(main_title)
        story.append(Spacer(1, 0.3 * inch))
        
        # Добавляем контент каждого изображения
        for i, image_data in enumerate(images_data, 1):
            # Заголовок для каждого изображения
            image_title = Paragraph(f"Image {i}: {image_data.get('filename', 'Unknown')}", subtitle_style)
            story.append(image_title)
            story.append(Spacer(1, 0.1 * inch))
            
            # Текст из изображения
            text_content = image_data.get('extracted_text', 'No text extracted')
            lines = text_content.split('\n')
            
            for line in lines:
                if line.strip():
                    p = Paragraph(line.strip(), normal_style)
                    story.append(p)
                    story.append(Spacer(1, 0.05 * inch))
            
            # Инфографика
            infographics = image_data.get('infographics', [])
            if infographics:
                story.append(Spacer(1, 0.1 * inch))
                info_title = Paragraph("Detected Infographics:", styles['Heading3'])
                story.append(info_title)
                
                for j, graphic in enumerate(infographics, 1):
                    graphic_text = f"{j}. Type: {graphic.get('type', 'unknown')}"
                    p = Paragraph(graphic_text, normal_style)
                    story.append(p)
            
            # Разрыв страницы между изображениями (кроме последнего)
            if i < len(images_data):
                story.append(PageBreak())
        
        doc.build(story)
        return True
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise e