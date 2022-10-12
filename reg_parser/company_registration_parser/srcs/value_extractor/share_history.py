

# -*- coding: utf-8 -*-


import re


class Share_History_Extractor:
    patten_stock_count = '\d+ 주'

    patten_change = re.compile('\d{4}\.\d{2}\.\d{2} 변경|   \.  \.   변경')
    patten_stock = "(?:전환상환우선주식(?:\w+| \w{1})|\w*전환우선주식(?:\w+| \w{1})|\w+주식\d? |\w+주\d? )"

    patten_register = '\d{4}\.\d{2}\.\d{2} 등기'

    patten_stock_price = '금 \d+ 원'
    patten_date = '\d{4}\.\d{2}\.\d{2}'
    patten_conut_re = "\d+ 주"

    stock_class_re = re.compile("(?:전환상환우선주식(?:\w+| \w{1})|\w*전환우선주식(?:\w+| \w{1})|\w+주식\d? |\w+주\d? )")

    stock_conut_re = re.compile("\d+ 주")

    total_capital_re = re.compile('금 \d+ 원')
    date_re = re.compile('\d{4}\.\d{2}\.\d{2}|    \.  \.   ')
    stock_issue_re = re.compile('\d+.주')

    current_stock_issue_pattern = re.compile('\d+ 원')
    change_date_pattern = re.compile('\d{4}\.\d{2}\.\d{2} 변경')
    change_date_pattern2 = re.compile('\d{4}\.\d{2}\.\d{2}')

    def __init__(self, idx, pdf_list, founded):
        self.founded = founded
        self.current_stock_issue_list = self.share_history_coverage_extractor(idx, pdf_list)

    def share_history_extractor(self):
        current_stock_issue_list = self.current_stock_issue_list
        current_stock_issue_list = [x for x in current_stock_issue_list if
                                    '발행주식의 총수와' not in x and '자본금의 액' not in x and '그 종류 및' not in x]

        for i in range(len(current_stock_issue_list) - 1):
            if re.compile(self.patten_stock_count).search(current_stock_issue_list[i].replace(',', '')) is None and \
                    current_stock_issue_list[i] != '':
                current_stock_issue_list[i] = current_stock_issue_list[i] + current_stock_issue_list[i + 1]
                current_stock_issue_list[i + 1] = ''
        current_stock_issue_list = list(filter(('').__ne__, current_stock_issue_list))

        share_lists = list()
        share_dict = dict()
        single_stocks = list()
        single_stock = dict()
        for idx, current_stock in enumerate(current_stock_issue_list):
            if '발행주식의 총수  ' in current_stock:
                if self.patten_change.search(current_stock):
                    status = '변경'

                elif '.  .' in current_stock:
                    status = '변경'

                else:
                    stock_status_candidate_list = current_stock_issue_list[idx:]
                    # stock_status_candidate_list = stock_status_candidate_list_raw[1:]
                    for status_idx, status_list in enumerate(stock_status_candidate_list):
                        if status_idx == 0:
                            continue
                        if '발행주식의 총수  ' in status_list:
                            break
                    stock_status_candidate_final_list = stock_status_candidate_list[:status_idx]

                    stock_status_pieces = list()
                    for stock_status_piece in stock_status_candidate_final_list:
                        stock_status_piece = stock_status_piece.replace(',', '').replace('발행주식의 총수', '')
                        stock_status_piece = re.sub(self.patten_conut_re,'',stock_status_piece)
                        stock_status_piece = re.sub(self.patten_register, '', stock_status_piece)
                        stock_status_piece = re.sub(self.patten_date, '', stock_status_piece)
                        stock_status_piece = re.sub(self.patten_stock, '', stock_status_piece)

                        stock_status_piece = re.sub(self.patten_stock_count, '', stock_status_piece)
                        stock_status_piece = re.sub(self.patten_stock_price, '', stock_status_piece)
                        stock_status_pieces.append(stock_status_piece)

                    status = ''.join([x.strip() for x in stock_status_pieces])
                if len(single_stocks):
                    share_dict["class"] = single_stocks
                    share_lists.append(share_dict)
                    single_stocks = []
                share_dict = dict()
                date = self.date_re.findall(current_stock)[0]
                if date == '    .  .   ':
                    date = self.founded
                share_dict["date"] = date.replace('.', '-')
                share_dict["status"] = status.strip()
                total_share = self.stock_issue_re.findall(current_stock.replace(',', ''))[0]
                share_dict["total_share"] = int(total_share.replace('주', '').strip())

            elif self.stock_class_re.search(current_stock) and '발행주식의 총수' not in current_stock:
                try:
                    share_type, count = (self.stock_class_re.findall(current_stock)[0],
                                         self.stock_conut_re.findall(current_stock.replace(',', ''))[0])
                    single_stock["share_type"] = share_type.strip()
                    single_stock["count"] = int(count.replace('주', '').strip())
                    single_stocks.append(single_stock)
                    single_stock = {}
                except:
                    continue
            if self.total_capital_re.search(current_stock.replace(',', '')):
                share_dict["total_capital"] = int(
                    self.total_capital_re.findall(current_stock.replace(',', ''))[0].replace('금', '').replace('원',
                                                                                                              '').strip())

        share_dict["class"] = single_stocks
        share_lists.append(share_dict)

        return share_lists

    def finite_company_share_history_extractor(self):
        current_stock_issue_join = ''.join(self.current_stock_issue_list)

        current_stock_dates = list()
        current_prices = list()
        for current_stock in ''.join(current_stock_issue_join).split('금 '):
            if '원' not in current_stock:
                continue
            if '원' in current_stock:
                price = int(self.current_stock_issue_pattern.findall(current_stock.replace(',', ''))[0].replace('원',
                                                                                                                '').strip())
                current_prices.append(price)
            if self.change_date_pattern.search(current_stock):
                date_piece = self.change_date_pattern2.findall(current_stock)[0]

                current_stock_dates.append(date_piece.replace('-',''))

        current_stock_date_list = [self.founded] + current_stock_dates

        return current_prices, current_stock_date_list

    def share_history_coverage_extractor(self, idx, pdf_list):
        units = [pdf_list[idx]]
        while True:
            idx = idx + 1
            if re.match('목\s+적', pdf_list[idx].strip()):
                break
            units.append(pdf_list[idx])
        return units