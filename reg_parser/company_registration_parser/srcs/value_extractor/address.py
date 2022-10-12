# -*- coding: utf-8 -*-
import re


class Address_Extractor:
    address_date_regex = re.compile('\d{4}\.\d{2}\.\d{2}|\.  \.   ')
    name_date_regex = re.compile('\d{4}\.\d{2}\.\d{2} (?:경정|변경|도로|행정|본점|착오|신청착오|이전|신청|주소)|    \.  \.   (?:경정|변경|도로|행정|본점|착오|신청착오|이전|신청|주소)')
    clean_date_regex = re.compile(
        '\d{4}\.\d{2}\.\d{2} (?:|신청착오|등기|변경|신청 착오|경정|도로|행정|본점|영문|이전|신청|착오|주소)|    \.  \.   (?:신청착오|등기|변경|신청 착오|경정|도로|행정|본점|착오 발견|영문|이전|신청|착오)|    \.  \.   ')
    head_office_change_regex = re.compile('\d{4}년 \d{2}월 \d{2}일')

    def __init__(self, idx, pdf_list, founded):
        self.founded = founded

        self.addresses_candidate_list = self.address_coverage_extractor(idx, pdf_list)
        # self.head_office_change_date = self.head_office_change_extractor(pdf_list)

    def address_dict_extractor(self):
        date_final_list = self.address_date_extractor()
        addresses_lists = self.address_extractor()
        address_final_list = list()
        for x in addresses_lists:
            address_final_list.append(x.replace('발견', '').replace('.', '').strip())
        address_final = [{"date": x, "address": y} for x, y in zip(date_final_list, address_final_list)]
        return address_final

    def address_extractor(self):
        addresses_candidate_list = self.addresses_candidate_list
        addresses_join = ''.join(addresses_candidate_list).replace('명주소', '').replace('본  점 ', '').replace('구역변경', '')
        date_pattern = re.compile('|'.join(self.name_date_regex.findall(addresses_join)))
        if len(date_pattern.pattern) == 0:
            addresses_list = [re.sub(self.clean_date_regex.pattern + '\.', '', addresses_join)]
        else:
            addresses_list = date_pattern.split(addresses_join)
            addresses_list = [re.sub(self.clean_date_regex.pattern + '\.', '', x).strip() for x in addresses_list]

        addresses_lists_final = [x.replace('명칭변경','').replace('등기','').replace('신청','').replace('착오','').replace('    ','').replace('   ','') for x in addresses_list if len(x)]
        return addresses_lists_final

    def address_date_extractor(self):
        addresses_candidate_list = self.addresses_candidate_list
        date_list_raw = [x for x in addresses_candidate_list if self.address_date_regex.search(x)]

        date_list_raw_join_list = [[date_list_raw[i], date_list_raw[i + 1]] for i in
                                   range(0, len(date_list_raw) - 1, 2)]
        date_final_list = list()
        for x, y in date_list_raw_join_list:
            if '.  .' in x:

                # if self.head_office_change_date:
                #     founded = self.head_office_change_date
                # else:
                founded = self.founded
                date = founded
            else:
                date = x.split(' ')[0].replace('.', '-')
            date_final_list.append(date)

        return date_final_list

    def address_coverage_extractor(self, idx, pdf_list):
        units = [pdf_list[idx]]
        while True:
            idx = idx + 1
            if '목          적' in pdf_list[idx] or '공고방법' in pdf_list[idx] or '출자 1좌의 금액' in pdf_list[idx] or '자본금의 액' in pdf_list[idx]:
                break
            units.append(pdf_list[idx])
            addresses_candidate_list = [x for x in units if x != '이전']
        return addresses_candidate_list
