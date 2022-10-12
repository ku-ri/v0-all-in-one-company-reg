# -*- coding: utf-8 -*-
import re

def extractor_corp_number_id(pdf_list):
    corp_number_id_regex = re.compile("\d{6}")

    for pdf_single in pdf_list:
        if '등기번호' in pdf_single:
            if len(corp_number_id_regex.findall(pdf_single)):
                cor_number_id = corp_number_id_regex.findall(pdf_single)[0].strip()
                break


    # cor_number_id  = [corp_number_id_regex.findall(x)[0].strip() for x in pdf_list if
    #  '등기번호' in x][0]

    return [cor_number_id]