# -*- coding: utf-8 -*-


import re


class Business_Type_Extractor:
    cor_object_number_patten_re = re.compile('\d{1,2}\.')

    def __init__(self, idx, pdf_list):

        self.cor_object_list = self.business_type_coverage_extractor(idx, pdf_list)

    def business_type_extractor(self):
        cor_object_list = self.cor_object_list

        cor_object_list2 = cor_object_list

        for i in range(len(cor_object_list)):
            if len(cor_object_list[i].split('<')[0].strip()) == 0:
                cor_object_list2[i - 1] = cor_object_list[i - 1] + cor_object_list[i]
                cor_object_list2[i] = ''

        cor_object_list2 = list(filter(('').__ne__, cor_object_list2))

        cor_object_list3 = [x for x in cor_object_list2 if '삭제' not in x]
        cor_object_list3 = [x for x in cor_object_list3 if
                            '부대하는 사업' not in x and '부대되는 사업' not in x and '부대사업' not in x and '부대 사업' not in x]

        cor_object_list4 = [x.split('<')[0].strip() for x in cor_object_list3 if len(x.split('<')[0].strip())]

        cor_object_join = ' '.join(cor_object_list4)
        cor_object_list_final = self.cor_object_number_patten_re.split(cor_object_join)
        cor_object_list_final = [x.strip().replace('"', "").replace("'", "") for x in cor_object_list_final if len(x.strip())]

        return cor_object_list_final

    def business_type_coverage_extractor(self, idx, pdf_list):
        units = list()
        while True:
            idx = idx + 1
            if '사원·청산인에 관한 사항' in pdf_list[idx] or '종류주식의 내용' in pdf_list[idx] or '임원에 관한' in pdf_list[idx] or '업무집행자·청산인에 관한 사항' in pdf_list[idx] or '기  타  사  항' in pdf_list[idx]:
                break
            units.append(pdf_list[idx])
        return units