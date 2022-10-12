# -*- coding: utf-8 -*-
import re


def extract_announced_date(pdf_list):
    open_date_regex = re.compile("\d{4}년\d{2}월\d{2}일")

    announced_date = \
    [open_date_regex.findall(x)[0].replace('년', '-').replace('월', '-').replace('일', '') for x in pdf_list if
     '열람일시' in x][0]

    return announced_date