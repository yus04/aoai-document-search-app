import re
from langchain.text_splitter import CharacterTextSplitter
from pdfminer.high_level import extract_text # 日本語対応テキスト抽出ライブラリ

def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path)
    return text

def main():
    pdf_path = '../input_data/20230609_policies_priority_outline_05.pdf'
    output_path = "../output_data/"
    text = extract_text_from_pdf(pdf_path)
    pages = text.split('\x0c')

    # セパレータで分割して、文字数でマージするTextSplitter
    text_splitter = CharacterTextSplitter(
        separator = "。",
        chunk_size = 200,
        chunk_overlap = 0,
    )
    
    for page_num, page_text in enumerate(pages, start=1):
        splited_page_text = text_splitter.split_text(page_text)
        for idx, text in enumerate(splited_page_text):
            with open(output_path + str(page_num) + "_" + str(idx) + ".txt", 'w', encoding='utf-8') as f:
                text = remove_newline(text)
                text = remove_space(text)
                text = remove_cid_tags(text)
                if text.endswith("・・"): continue # エラー回避
                f.write(text)
        print(f'Page {page_num} text extracted and saved.')

def remove_newline(text: str) -> str:
    text = text.replace('\r\n', '')
    text = text.replace('\n', '')
    return text

def remove_space(text: str) -> str:
    text = text.replace(' ', '')
    return text

def remove_cid_tags(input_string: str) -> str:
    cleaned_string = re.sub(r'\(cid:\d+\)', '', input_string)
    return cleaned_string

if __name__ == "__main__":
    main()
