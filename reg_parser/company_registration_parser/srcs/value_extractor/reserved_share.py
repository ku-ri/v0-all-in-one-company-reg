# -*- coding: utf-8 -*-

import re


class Reserved_Share_Extractor:
    patten_register = '\d{4}\.\d{2}\.\d{2} 등기|   \.  \.   등기'
    patten_date = '\d{4}\.\d{2}\.\d{2}'

    stock_count_re = re.compile('\d+ 주')
    patten_stock_count_re = re.compile('\d+ ?주')

    date_re1 = re.compile('\d{4}\.\d{2}\.\d{2} (?:등기)|    \.  \.   (?:등기)|    \.  \.   ')
    date_re2 = re.compile('\d{4}\.\d{2}\.\d{2}|    \.  \.   ')

    def __init__(self, idx, pdf_list, founded):
        self.founded = founded
        self.stock_issue_list = self.reserved_share_coverage_extractor(idx, pdf_list)

    def reserved_share_dict_extractor(self):

        total_share_list = self.total_share_extractor()
        date_issue_list = self.share_date_extractor()
        stock_issue_event_list_final = self.stock_issue_extractor()

        num_short1 = len(total_share_list) - len(date_issue_list)

        if num_short1:
            add_date = [self.founded] * num_short1
            date_issue_list = add_date + date_issue_list

        num_short2 = len(total_share_list) - len(stock_issue_event_list_final)

        if num_short2:
            add_state = ['변경'] * num_short2
            stock_issue_event_list_final = add_state + stock_issue_event_list_final
        total_share_dicts = list()
        for x, y, z in zip(total_share_list, date_issue_list, stock_issue_event_list_final):
            total_share_dicts.append(
                {"total_share": x, "date": y.replace('변경', '').replace('.', '-').strip(), "status": z})

        return total_share_dicts

    def share_date_extractor(self):
        stock_issue_join = ''.join(
            self.date_re1.split(' '.join(self.stock_issue_list).replace('발행할 주식의 총수', '').replace(',', '')))

        stock_issue_list_final = self.date_re2.findall(stock_issue_join)

        return stock_issue_list_final

    def total_share_extractor(self):
        total_share_list_final = [
            int(self.patten_stock_count_re.findall(x.replace(',', ''))[0].replace('주', '').strip()) for x in
            self.stock_issue_list if ' 주' in x]

        return total_share_list_final

    def stock_issue_extractor(self):
        stock_issue_join = ''.join(self.stock_issue_list).replace('발행할 주식의 총수', '').replace(',', '')
        stock_issue_event_list = self.stock_count_re.split(stock_issue_join)
        stock_issue_event_list = ' '.join(stock_issue_event_list)
        stock_issue_event_list = re.sub(self.patten_register, '', stock_issue_event_list)
        stock_issue_event_list = re.sub(self.patten_date, '', stock_issue_event_list)
        stock_issue_event_list = stock_issue_event_list.replace('.', '')
        stock_issue_event_list = stock_issue_event_list.strip() + ' '
        stock_issue_event_list = stock_issue_event_list.split('변경 ')
        stock_issue_event_list_final = [x if len(x.strip()) else x + '변경' for x in stock_issue_event_list]
        stock_issue_event_list_final = ['변경' if x.strip() == '등기' else x.strip() for x in stock_issue_event_list_final]

        return stock_issue_event_list_final

    def reserved_share_coverage_extractor(self, idx, pdf_list):
        units = [pdf_list[idx]]
        while True:
            idx = idx + 1
            if '발행주식의' in pdf_list[idx]:
                break
            units.append(pdf_list[idx])
        return units