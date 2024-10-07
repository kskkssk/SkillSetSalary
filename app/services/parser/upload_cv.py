from pypdf import PdfReader


def upload(pdf_path):
    reader = PdfReader(pdf_path)
    all_text = ''
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text()
        if text:
            all_text += text + '\n'
    return all_text
