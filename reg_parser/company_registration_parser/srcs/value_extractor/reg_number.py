# -*- coding: utf-8 -*-

import re


def extractor_reg_number(pdf_content):
    reg_number_regex = re.compile('\d+-\d+')
    reg_number = reg_number_regex.findall(pdf_content)[0]

    return reg_number