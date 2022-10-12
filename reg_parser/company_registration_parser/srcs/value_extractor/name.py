# -*- coding: utf-8 -*-

import re


class Name_Extractor:
    cor_name_date_patten_re = re.compile('\d{4}\.\d{2}\.\d{2}|\.  \.   ')

    cor_name_change_patten_re = re.compile('\d{4}\.\d{2}\.\d{2} (?!등기|경정)\D{2}|\.  \.   (?!등기|경정)\D{2}|[\.  \.]$')
    cor_name_register_patten_re = re.compile('\d{4}\.\d{2}\.\d{2} (?:등기|경정)|\.  \.   (?:등기|경정)')
    cor_name_register_patten_re2 = re.compile('상  호')
    eng_name_re = "\(.+\)"
    cor_type_re = re.compile('\w+회사')
    hangul = '[ㄱ-ㅣ가-힣]+'

    def __init__(self, idx, pdf_list, founded):
        self.founded = founded

        self.cor_names = self.name_coverage_extractor(idx - 1, pdf_list)

    def name_dict_extractor(self):
        name_dicts = list()

        name_dict = dict()
        data_status_list_name = self.name_date_extractor()
        names_list = self.name_clean_extractor()

        for date, name_candidate in zip(data_status_list_name, names_list):
            name_dict['date'] = date
            name_raw = re.sub('사회복지법인|학교법인|의료법인|사단법인|재단법인|어업회사법인|어업회사법인|농업회사 법인|농업회사|합명회사|농업회사법인|유한책임회사|주식회사|유한회사|신청|착오', '', name_candidate)
            kor_name = re.sub(self.eng_name_re + '|\,|\.', '', name_raw).strip().replace(' ', '')
            kor_name = re.sub(r'명칭', '', kor_name)
            name_dict["kor"] = kor_name.replace('( 지점 )', '').strip()

            if '주식회사' in name_candidate:
                cor_type = '주식회사'
                name_dict["cor_type"] = cor_type

            elif '합명회사' in name_candidate:
                cor_type = '합명회사'
                name_dict["cor_type"] = cor_type

            elif '유한회사' in name_candidate:
                cor_type = '유한회사'
                name_dict["cor_type"] = cor_type
            elif self.cor_type_re.search(name_candidate):
                cor_type = ''.join(self.cor_type_re.findall(name_candidate))
                if len(cor_type.strip()):
                    name_dict["cor_type"] = cor_type.strip()
            if '(' in name_raw:
                name_raw = re.sub(self.hangul, '', name_raw).strip()
                eng_name = name_raw.split('(')[1].strip().split(')')[0].strip()
                if len(eng_name):
                    if eng_name != '지점':
                        eng_name = re.sub(self.hangul, '', eng_name)
                        eng_name = re.sub('Incorporated|CORPORATION|Corporation|Incorporated|INCORPORATED', '', eng_name)
                        eng_name = re.sub('co,|CO,|Co,', ' ', eng_name)
                        eng_name = re.sub('co\.|CO\.|Co\.', ' ', eng_name)
                        eng_name = re.sub(
                            ',InC|,Inc|,inc|,INC|,lnc| InC| Inc| inc| INC| lnc|InC\.|Inc\.|inc\.|INC\.|lnc\.|LLC|\.Inc|\.Inc|I nc',
                            '', eng_name)
                        eng_name = re.sub(',Ltd|,LTD|,ltd|,INC| Ltd| LTD| ltd| INC|Ltd\.|LTD\.|ltd\.|INC\.|\.Ltd', '',
                                          eng_name)
                        eng_name = re.sub(' CORP| Corp| corp|\.|\,', '', eng_name).strip()
                        if eng_name.strip()[-1] == '.':
                            eng_name = eng_name.strip()[:-1]
                        if eng_name.strip()[-1] == '.':
                            eng_name = eng_name.strip()[:-1]
                        name_dict["eng"] = eng_name.replace("'","")

            name_dicts.append(name_dict)
            name_dict = dict()

        return name_dicts

    def name_date_extractor(self):
        date_list_raw = [x for x in self.cor_names if self.cor_name_date_patten_re.search(x)]

        date_list_raw_join_list = [[date_list_raw[i], date_list_raw[i + 1]] for i in
                                   range(0, len(date_list_raw) - 1, 2)]
        data_status_list_name = list()
        for x, y in date_list_raw_join_list:
            if '.  .' in x:
                date = self.founded
            else:
                date = x.split(' ')[0].replace('.', '-')

            data_status_list_name.append(date)

        return data_status_list_name

    def name_clean_extractor(self):

        cor_names = self.cor_names
        for i, cor_name_candidate in enumerate(cor_names):

            if '(' in cor_name_candidate and ')' not in cor_name_candidate:
                cor_names[i] = ''.join(cor_names[i:i + 3:2]).strip()
                cor_names[i + 2] = ''

        cor_names = list(filter(('').__ne__, cor_names))

        cor_names_clean = [x for x in cor_names if self.cor_name_change_patten_re.search(
            x.strip()) is None or self.cor_name_register_patten_re2.search(x) if x!='착오']

        cor_names_index = [0]
        for x in cor_names_clean:

            if self.cor_name_register_patten_re.search(x):
                cor_names_index.append(cor_names_clean.index(x) + 1)

            if self.cor_name_register_patten_re2.search(x):
                cor_names_index.append(cor_names_clean.index(x) + 2)

        # cor_names_index = list(set(cor_names_index[:-1]))
        cor_names_index = list(range(0, len(cor_names_clean), 2))

        names_clean_list = list()
        for i in cor_names_index:
            if i < len(cor_names_clean):
                cor_name_final = cor_names_clean[i].replace('상  호', '').strip()
                if self.cor_name_register_patten_re.search(cor_name_final):
                    cor_name_final = cor_names_clean[i - 1].replace('상  호', '').strip()
                if self.cor_name_date_patten_re.search(cor_name_final):
                    continue
                names_clean_list.append(cor_name_final)
        if len(names_clean_list) == 0:
            new_cor_names = [x.replace('.', '').replace('명  칭', '').replace('상  호', '').strip() for x in self.cor_names]
            names_clean_list = [x for x in new_cor_names if len(x)]
        return names_clean_list

    def name_coverage_extractor(self, idx, pdf_list):
        units = [pdf_list[idx]]
        while True:
            idx = idx + 1

            if '본  점' in pdf_list[idx] or '주사무소' in pdf_list[idx]:
                break
            units.append(pdf_list[idx])
        return units[:-1]