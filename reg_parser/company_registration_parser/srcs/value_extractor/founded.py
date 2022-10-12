# -*- coding: utf-8 -*-

import re

def extractor_founded(pdf_list):
    cor_founded_regex = re.compile('\d{4} 년  \d{2} 월  \d{2} 일')

    for idx, line in enumerate(pdf_list):
        if '회사성립연월일 ' in line or '법인성립연월일' in line:
            line = pdf_list[idx] + '      '+ pdf_list[idx+1]
            founded = cor_founded_regex.findall(line)[-1].replace(' 년  ', '-').replace(' 월  ', '-').replace('일', '').strip()

    # founded = \
    # [cor_founded_regex.findall(x)[0].replace(' 년  ', '-').replace(' 월  ', '-').replace('일', '') for x in pdf_list if
    #  '회사성립연월일 ' in x or '법인성립연월일' in x][0].strip()
    return founded