'''
Author: GimTaeGyun gtgyun@bflysoft.com
Date: 2024-08-21 15:32:10
LastEditors: GimTaeGyun gtgyun@bflysoft.com
LastEditTime: 2024-08-21 16:22:44
'''
import olefile
import zlib
import struct
import unicodedata
import re
    
class HWPExtractor(object):
    FILE_HEADER_SECTION = "FileHeader"
    HWP_SUMMARY_SECTION = "\x05HwpSummaryInformation"
    SECTION_NAME_LENGTH = len("Section")
    BODYTEXT_SECTION = "BodyText"
    HWP_TEXT_TAGS = [67]

    def __init__(self, filename):
        self._ole = self.load(filename)
        self._dirs = self._ole.listdir()

        self._valid = self.is_valid(self._dirs)
        if not self._valid:
            raise Exception("Not Valid HwpFile")
        
        self._compressed = self.is_compressed(self._ole)
        self.text = self._get_text()
    
    # 파일 불러오기 
    def load(self, filename):
        return olefile.OleFileIO(filename)
    
    # hwp 파일인지 확인 header가 없으면 hwp가 아닌 것으로 판단하여 진행 안함
    def is_valid(self, dirs):
        if [self.FILE_HEADER_SECTION] not in dirs:
            return False

        return [self.HWP_SUMMARY_SECTION] in dirs

    # 문서 포맷 압축 여부를 확인
    def is_compressed(self, ole):
        header = self._ole.openstream("FileHeader")
        header_data = header.read()
        return (header_data[36] & 1) == 1

    # bodytext의 section들 목록을 저장
    def get_body_sections(self, dirs):
        m = []
        for d in dirs:
            if d[0] == self.BODYTEXT_SECTION:
                m.append(int(d[1][self.SECTION_NAME_LENGTH:]))

        return ["BodyText/Section"+str(x) for x in sorted(m)]
    
    # text를 뽑아내는 함수
    def get_text(self):
        return self.text

    # 전체 text 추출
    def _get_text(self):
        sections = self.get_body_sections(self._dirs)
        text = ""
        for section in sections:
            text += self.get_text_from_section(section)
            text += "\n"

        self.text = text
        return self.text

    # section 내 text 추출
    def get_text_from_section(self, section):
        bodytext = self._ole.openstream(section)
        data = bodytext.read()

        unpacked_data = zlib.decompress(data, -15) if self._compressed else data
        size = len(unpacked_data)

        i = 0

        text = ""
        while i < size:
            header = struct.unpack_from("<I", unpacked_data, i)[0]
            rec_type = header & 0x3ff
            level = (header >> 10) & 0x3ff
            rec_len = (header >> 20) & 0xfff

            if rec_type in self.HWP_TEXT_TAGS:
                rec_data = unpacked_data[i+4:i+4+rec_len]
                
                # 정제 추가된 부분
                decode_text = rec_data.decode('utf-16')
                # 문자열을 담기 전 정제하기
                res = self.remove_control_characters(self.remove_chinese_characters(decode_text))
                
                text += res
                text += "\n"

            i += 4 + rec_len

        return text

    # 텍스트 정제 함수
    def remove_chinese_characters(self, s: str):   
        return re.sub(r'[\u4e00-\u9fff]+', '', s)
        
    def remove_control_characters(self, s):    
        return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")