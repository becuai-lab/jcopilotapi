 
import zipfile
import xml.etree.ElementTree as ET
from jcopilot.util.HWPExtractor import HWPExtractor
import tempfile
import pymupdf as fitz

class CommonExtractor(object):
     
    # text 추출 함수 -> 이 함수를 사용하면 됨
    def extract_text_from_hwp(filename):
        hwp = HWPExtractor(filename) 
        return hwp.get_text() 

    def extract_text_from_hwpx(file_path):
        try:
            hwpx_file = zipfile.ZipFile(file_path)
            section0 = hwpx_file.read("Contents/section0.xml").decode()

            root = ET.fromstring(section0)

            texts = []
            for t in root.iterfind('.//hp:t', namespaces={'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph'}):
                if t.text:  # None이 아닌 경우에만 처리
                    text = t.text.strip()
                    if text:  # 공백이 아닌 경우에만 추가
                        texts.append(text)        
            return ' '.join(texts)
        except Exception as e:
            print(f"HWPX 파일 파싱 중 오류가 발생했습니다: {str(e)}")
            # st.error(f"HWPX 파일 파싱 중 오류가 발생했습니다: {str(e)}")
            return ""   

    def extract_text_from_pdf(file_data):
        try:
            
            # pdf_file = uploaded_file.file.read()
            # 파일 스트림을 사용하여 PDF 열기
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file_data)
                temp_file_path = temp_file.name
            
            # temp 파일을 fitz로 열기
            doc = fitz.open(temp_file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            
            # os.remove(temp_file_path)  # 임시 파일 삭제
            return text
        except Exception as e:
            print(f"PDF 파일 처리 중 오류가 발생했습니다: {str(e)}")
            # st.error(f"PDF 파일 처리 중 오류가 발생했습니다: {str(e)}")
            return ""