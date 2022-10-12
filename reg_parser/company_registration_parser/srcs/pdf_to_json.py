# -*- coding: utf-8 -*-

from .pdf_to_text.pdf_reader import Pdf_To_Text_Paser
from .value_extractor.corp_number_id import extractor_corp_number_id
from .value_extractor.announced_date import extract_announced_date
from .value_extractor.reg_number import extractor_reg_number

from .value_extractor.file_url import extractor_file_url

from .value_extractor.founded import extractor_founded
from .value_extractor.name import Name_Extractor
from .value_extractor.address import Address_Extractor
from .value_extractor.share_price import Share_Price_Extractor
from .value_extractor.reserved_share import Reserved_Share_Extractor
from .value_extractor.share_history import Share_History_Extractor
from .value_extractor.business_type import Business_Type_Extractor
from .value_extractor.board_members import Board_Members_Extractor, Board_Members_Staff_Extractor
from .value_extractor.status import Status_Extractor
from .command import Executor

import re

class Pdf_To_Json:
    corp_number_id_passing_true = False
    current_stock_passing_true = False
    reg_number_passing_true = False
    name_passing_true = False
    address_passing_true = False
    one_stock_passing_true = False
    stock_issue_passing_true = False
    cor_object_passing_True = False
    board_passing_true = False
    cor_make_passing_true = False




    def __init__(self, file_name, pdf_open):
        self.file_name = file_name
        self.pdf_to_text_paser = Pdf_To_Text_Paser(file_name)
        try:
            self.pdf_list = self.pdf_to_text_paser.pdf_to_text(pdf_open)
            self.file_name = file_name
        except:
            # 세션 관리
            sql = "SELECT pg_terminate_backend(pid)  FROM pg_stat_activity  WHERE state ILIKE 'idl%' AND usename ILIKE ('api_company_reg%')"
            executor = Executor()
            curs = executor.conn.cursor()
            curs.execute(sql)
            executor.conn.close()
            pass

    def start(self):


        error_list = []

        cor_data = dict()

        file_url = extractor_file_url(self.file_name)

        cor_data["file_url"] = file_url

        try:
            announced_date = extract_announced_date(self.pdf_list)
            cor_data["announced_date"] = announced_date
        except Exception as e:
            print('error in announced_date: ' + str(e))
            print(self.file_name)
            error_list.append('announced_date')

        try:
            corp_number_id = extractor_corp_number_id(self.pdf_list)
            cor_data["corp_number_id"] = corp_number_id
        except Exception as e:
            print('error in corp_number_id: ' + str(e))
            print(self.file_name)
            # 세션 관리
            sql = "SELECT pg_terminate_backend(pid)  FROM pg_stat_activity  WHERE state ILIKE 'idl%' AND usename ILIKE ('api_company_reg%')"
            executor = Executor()
            curs = executor.conn.cursor()
            curs.execute(sql)
            executor.conn.close()
            raise IndexError

        pdf_list = self.delete_in_pdf_garbage(self.pdf_list)

        try:
            founded = extractor_founded(pdf_list)
            cor_data["founded"] = founded
            reg_founded_idx = [idx for idx, x in enumerate(pdf_list) if '등기기록의 개설 사유 및 연월일' in x]
            if len(reg_founded_idx):
                reg_founded_date_raw = re.findall('\d{4}년\d{2}월\d{2}일등기', ' '.join(pdf_list[reg_founded_idx[0]+1:reg_founded_idx[0]+6]).replace(' ', ''))
            if len(reg_founded_idx) and len(reg_founded_date_raw):
                founded_date_raw = reg_founded_date_raw[0]
                founded = founded_date_raw.replace('년','-').replace('월','-').replace('일등기','')

        except Exception as e:
            founded = '0000-00-00'
            cor_data["founded"] = '0000-00-00'

            print('error in founded: ' + str(e))
            print(self.file_name)
            error_list.append('founded')

        if '기  타  사  항' in ' '.join(pdf_list):
            break_true = False
        else:
            break_true = True
        for idx, pdf_content in enumerate(pdf_list):

            if '등록번호' in pdf_content:
                try:
                    if self.reg_number_passing_true:
                        pass
                    else:
                        self.reg_number_passing_true = True
                        corp_number = extractor_reg_number(pdf_content)
                        cor_data["corp_number"] = corp_number
                except Exception as e:
                    raise IndexError
                    print('error in corp_number: ' + str(e))
                    print(self.file_name)

            if '상  호' in pdf_content or '명  칭' in pdf_content:
                try:
                    if self.name_passing_true:
                        pass
                    else:
                        self.name_passing_true = True
                        name_extractor = Name_Extractor(idx, pdf_list, cor_data["founded"] )
                        name_dicts = name_extractor.name_dict_extractor()
                        cor_data["name"] = name_dicts

                except Exception as e:
                    print('error in name: ' + str(e))
                    print(self.file_name)
                    error_list.append('name')

                    pass
            if '본  점' in pdf_content or '주사무소' in pdf_content:
                try:
                    if self.address_passing_true:
                        pass
                    else:
                        self.address_passing_true = True
                        address_extractor = Address_Extractor(idx, pdf_list, founded)

                        address_dicts = address_extractor.address_dict_extractor()
                        cor_data["address"] = address_dicts

                        address_17_cities = ["대구광역시","대전광역시", "경상남도","경상북도",\
                                             "세종시","세종특별자치시", "부산광역", "서울특별시","충청북도","충청남도",\
                                             "경기도","울산광역시","강원도", "제주특별자치도","전라남도","전라북도","광주광역시"]
                        for one_address in cor_data["address"]:
                            count_city_one_address = sum([one_address['address'].count(city) for city in address_17_cities])
                            if count_city_one_address >= 2:
                                print('error in address')
                                print(self.file_name)
                                error_list.append('address')
                                break



                except Exception as e:
                    print('error in address: ' + str(e))
                    print(self.file_name)
                    error_list.append('address')

                    pass

            if '1주의 금액' in pdf_content or '출자 1좌의 금액' in pdf_content:
                try:
                    if self.one_stock_passing_true:
                        pass
                    else:
                        self.one_stock_passing_true = True

                        share_price_extractor = Share_Price_Extractor(idx, pdf_list, founded)
                        one_prices, one_stock_date_list = share_price_extractor.one_stock_date_extractor()

                        if len(one_prices) + len(one_stock_date_list):
                            cor_data["share_price"] = [{"price": x, "date": y} for x, y in
                                                       zip(one_prices, one_stock_date_list)]
                except Exception as e:
                    print('error in share_price: ' + str(e))
                    print(self.file_name)
                    error_list.append('share_price')

                    pass

            if '발행할 주식의 총수' in pdf_content:
                try:
                    if self.stock_issue_passing_true:
                        pass
                    else:
                        self.stock_issue_passing_true = True
                        reserved_share_extractor = Reserved_Share_Extractor(idx - 1, pdf_list, founded)
                        total_share_dicts = reserved_share_extractor.reserved_share_dict_extractor()

                        cor_data["reserved_share"] = total_share_dicts
                except Exception as e:
                    print('error in reserved_share: ' + str(e))
                    print(self.file_name)
                    error_list.append('reserved_share')

                    pass
            if '발행주식의 총수와' in pdf_content:

                try:
                    if self.current_stock_passing_true:
                        continue

                    else:
                        self.current_stock_passing_true = True
                        share_history_extractor = Share_History_Extractor(idx, pdf_list, founded)
                        share_history_lists = share_history_extractor.share_history_extractor()
                        cor_data["share_history"] = share_history_lists

                except Exception as e:
                    print('error in share_history: ' + str(e))
                    print(self.file_name)
                    error_list.append('share_history')
                    pass

            if '자본금의 총액' in pdf_content or '자본금의 액' in pdf_content:
                try:
                    if self.current_stock_passing_true:
                        continue
                    else:
                        share_history_extractor = Share_History_Extractor(idx, pdf_list, founded)
                        current_prices, current_stock_date_list = share_history_extractor.finite_company_share_history_extractor()

                        if len(current_prices) + len(current_stock_date_list):
                            cor_data["share_history"] = [{"total_capital": x, "date": y} for x, y in
                                                         zip(current_prices, current_stock_date_list)]
                except Exception as e:
                    print('error in share_history: ' + str(e))
                    print(self.file_name)
                    # cor_data['error'] = 'share_history'
                    error_list.append('share_history')
                    pass

            if re.match('목\s+적', pdf_content.strip()):
                try:
                    if self.cor_object_passing_True:
                        pass
                    else:
                        self.cor_object_passing_True = True
                        business_type_extractor = Business_Type_Extractor(idx, pdf_list)
                        cor_object_list_final = business_type_extractor.business_type_extractor()

                        cor_data["business_type"] = cor_object_list_final
                except Exception as e:
                    print('error in business_type: ' + str(e))
                    print(self.file_name)
                    error_list.append('business_type')

                    pass

            if '임원에 관한' in pdf_content or '업무집행자·청산인에 관한 사항' in pdf_content:
                try:
                    if self.board_passing_true:
                        pass
                    else:
                        self.board_passing_true = True

                        board_members_extractor = Board_Members_Extractor(idx, pdf_list, cor_data["founded"])

                        person_dicts, name_error, nationality_error, birthday_error = board_members_extractor.board_members_extractor()
                        if name_error:
                            error_list.append('board_members_name')

                        if nationality_error:
                            error_list.append('board_members_nationality')

                        if birthday_error:
                            error_list.append('board_members_birthday')

                        cor_data["board_members"] = person_dicts

                        if break_true:
                            break

                except Exception as e:
                    print('error in board_members: ' + str(e))
                    print(self.file_name)
                    error_list.append('board_members')

                    pass

            if '사원·청산인에 관한 사항' in pdf_content:
                try:
                    if self.board_passing_true:
                        pass
                    else:
                        self.board_passing_true = True

                        board_members_extractor = Board_Members_Staff_Extractor(idx, pdf_list, cor_data["founded"])

                        person_dicts, name_error, nationality_error, birthday_error = board_members_extractor.board_members_extractor()
                        if name_error:
                            error_list.append('board_members_name')

                        if nationality_error:
                            error_list.append('board_members_nationality')

                        if birthday_error:
                            error_list.append('board_members_birthday')

                        cor_data["board_members"] = person_dicts

                        if break_true:
                            break

                except Exception as e:
                    print('error in board_members: ' + str(e))
                    print(self.file_name)
                    error_list.append('board_members')

                    pass

            if '기  타  사  항' in pdf_content:
                try:
                    status_extractor = Status_Extractor(idx, pdf_list)
                    status_dicts = status_extractor.status_extractor()
                    cor_data["status"] = status_dicts
                    break


                except Exception as e:
                    print('error in status: ' + str(e))
                    print(self.file_name)
                    error_list.append('status')

                    pass

        if len(error_list):
            cor_data['error'] = ','.join(error_list)
        return cor_data

    def delete_in_pdf_garbage(self, pdf_list):
        pdf_list = [x for x in pdf_list if '열람일시' not in x and '등기번호' not in x]

        return pdf_list
