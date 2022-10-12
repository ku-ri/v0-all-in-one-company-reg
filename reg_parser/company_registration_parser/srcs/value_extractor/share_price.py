# -*- coding: utf-8 -*-


import re


class Share_Price_Extractor:
    one_pattern = re.compile('\d+ 원')
    change_date_pattern = re.compile('\d{4}\.\d{2}\.\d{2} 변경')
    change_date_pattern2 = re.compile('\d{4}\.\d{2}\.\d{2}')

    def __init__(self, idx, pdf_list, founded):

        self.founded = founded
        self.one_stock_list = self.one_stock_coverage_extractor(idx, pdf_list)

    def one_stock_date_extractor(self):
        one_stock_dates = list()
        one_prices = list()
        for one_stock in ' '.join(self.one_stock_list).split('금'):
            if '원' not in one_stock:
                continue
            if '원' in one_stock:
                price = one_stock.replace(',', '')
                price = int(self.one_pattern.findall(price)[0].replace('원', '').strip())
                one_prices.append(price)
            if self.change_date_pattern.search(one_stock):
                date_piece1 = self.change_date_pattern.findall(one_stock)[0]
                date_piece2 = self.change_date_pattern2.findall(one_stock)[0]

                one_stock_dates.append(date_piece2.replace('.', '-'))

        one_stock_date_list = [self.founded] + one_stock_dates

        return one_prices, one_stock_date_list

    def one_stock_coverage_extractor(self, idx, pdf_list):
        units = [pdf_list[idx]]
        while True:
            idx = idx + 1

            if '발행할 주식의 총수' in pdf_list[idx] or '자본금의 총액' in pdf_list[idx] or '자본금의 액' in pdf_list[idx]:
                break
            units.append(pdf_list[idx])
        return units