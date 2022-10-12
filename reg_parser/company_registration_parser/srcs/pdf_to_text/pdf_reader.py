# -*- coding: utf-8 -*-

import pdfplumber
import os
from io import BytesIO

class Pdf_To_Text_Paser:
     def __init__(self, file_name):
          self.file_path = os.path.join(file_name)
     def pdf_to_text(self, pdf_open):

          pdf = pdfplumber.open(BytesIO(pdf_open))

          pdf_list = []
          for pdf in pdf.pages:
              text = pdf.extract_text()
              text_list = text.split('\n')
              pdf_list = pdf_list + text_list
              pdf_list = self.delete_in_pdf_garbage(pdf_list)

          return pdf_list
     
     def delete_in_pdf_garbage(self,pdf_list):
          if '열 람 용' in pdf_list:
               pdf_list.remove('열 람 용')
          pdf_list = [x.replace('열 ','').replace('람 ','').replace('용 ','') if '열 ' in x and '람 ' in x and '용 ' in x else x for x in pdf_list]
           
          pdf_list = [x.replace('열','').replace('람','').replace('용','') if '열' in x and '람' in x and '용' in x else x for x in pdf_list]
          pdf_list = [x.replace('신','').replace('청','').replace('사','').replace('건','').replace('처','').replace('리','').replace('중','') if '신' in x and '청' in x and '사' in x and '건' and '처' in x and '리' in x and '중' in x else x for x in pdf_list]
           
          pdf_list = [x for x in pdf_list if '실선으로 그어진 부분은' not in x and '신청사건처리중' not in x]


          return pdf_list



