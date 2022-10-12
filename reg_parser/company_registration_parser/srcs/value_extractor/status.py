# -*- coding: utf-8 -*-
import re


class Status_Extractor:
    etc_date_re = re.compile("\d{4} 년  \d{2} 월  \d{2} 일")

    def __init__(self, idx, pdf_list):
        self.pdf_candidate_list = pdf_list[idx + 1:]

    def status_extractor(self):
        status_dicts = list()
        for pdf_idx, pdf_candidate in enumerate(self.pdf_candidate_list):

            if '존립기간 또는 해산사유' in pdf_candidate or '해산 사유가 발생한 경우' in pdf_candidate:
                continue
            # if '해산 사유가 발생한 경우' in pdf_candidate:
            #     continue

            if ('회사계속' in pdf_candidate and '1.' in pdf_candidate) or (
                    '청산' in pdf_candidate and '1.' in pdf_candidate) or (
                    '파산' in pdf_candidate and '1.' in pdf_candidate) or (
                    '회생' in pdf_candidate and '1.' in pdf_candidate) or (
                    '분할' in pdf_candidate and '1.' in pdf_candidate) or (
                    '해산' in pdf_candidate and '1.' in pdf_candidate) or (
                    '합병' in pdf_candidate and '1.' in pdf_candidate):
                if len(pdf_candidate) > 40:
                    continue

                status_dict = dict()
                status_dict["status"] = ' '.join(pdf_candidate.split()[1:]).replace('"', "").replace("'", "")
                pdf_candidate_list2 = self.pdf_candidate_list[pdf_idx + 1:]
                for pdf_idx2, pdf_candidate2 in enumerate(pdf_candidate_list2):
                    if '전   환   사   채' in pdf_candidate2 or '1. ' in pdf_candidate2 or '등기' in pdf_candidate2 or '동일폐쇄' in pdf_candidate2 or '주 식 매 수 선 택 권' in pdf_candidate2 or '회사성립연월일' in pdf_candidate2:
                        reason_join = ''.join(pdf_candidate_list2[:pdf_idx2]).strip()
                        if pdf_idx2 > 7:
                            break
                        if len(self.etc_date_re.findall(pdf_candidate_list2[pdf_idx2])):
                            date = self.etc_date_re.findall(pdf_candidate_list2[pdf_idx2])[0].replace(' ', '').replace(
                                '년', '-').replace('월', '-').replace('일', '')
                            status_dict["date"] = date

                        reason = reason_join.strip()
                        status_dict["status_reason"] = reason.replace('"', "").replace("'", "")
                        status_dicts.append(status_dict)
                        break
        return status_dicts