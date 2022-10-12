from .company_address import address_update
from .namehistory import namehistory_update
from .s3manager import S3Manager
from APIserver.decorator import apiValidate

import psycopg2 as pg2
import os, json
from datetime import date
from datetime import datetime

import timeit
import re
import logging
import operator
import collections

logger = logging.getLogger(__name__)


class Executor(object):
    def __init__(self):
        self.conn = pg2.connect(database=os.environ['DB_NAME'], user=os.environ['DB_USER'],
                                password=os.environ['DB_PW'], host=os.environ['MASTER_DB_HOST'],
                                port=os.environ['DB_PORT'])

        self.conn_api = pg2.connect(database=os.environ['DB_API_NAME'], user=os.environ['DB_API_USER'],
                                    password=os.environ['DB_API_PW'], host=os.environ['MASTER_DB_HOST'],
                                    port=os.environ['DB_PORT'])

    def run(self, options):
        print('start ', options['pdf_path'])
        from .pdf_to_json import Pdf_To_Json
        pdf_to_json = Pdf_To_Json(options['pdf_path'], options["pdf_open"])
        cor_data = pdf_to_json.start()

        return cor_data

    @staticmethod
    def update_db_json(cor_data, old_db_data):
        for key in cor_data.keys():

            if key in ['status', 'error', 'update_date', 'file_url', 'corp_number']:
                old_db_data[key] = cor_data[key]
                continue
            else:
                if key in old_db_data:
                    old_db_items = old_db_data[key]
                    new_db_items = cor_data[key]
                else:
                    old_db_data[key] = cor_data[key]
                    continue
                if isinstance(old_db_items, str) or key in ['corp_number_id', 'file_url', 'business_type']:
                    continue

            if key != 'board_members':
                gap_data = [x for x in new_db_items + old_db_items if x not in new_db_items or x not in old_db_items]
                old_db_data[key] = old_db_data[key] + gap_data

                old_db_data[key] = sorted(old_db_data[key], key=lambda k: k['date'])


            elif key == 'board_members':
                board_member_names = [x['name'] for x in old_db_items]
                for new_board_member_data in new_db_items:
                    if new_board_member_data['name'] in board_member_names:
                        board_member_index = board_member_names.index(new_board_member_data['name'])
                        old_db_data[key][board_member_index]['action'] = \
                            old_db_data[key][board_member_index]['action'] + new_board_member_data['action']
                    else:
                        old_db_data[key] = old_db_data[key] + [new_board_member_data]

        return old_db_data

    def order_duplicate_check(self, cor_data):
        for key in cor_data:
            if len(cor_data[key]):
                if type(cor_data[key][0]) != dict:
                    continue
            else:
                continue

            if key == 'board_members':
                for board_member in cor_data['board_members']:

                    if board_member['nationality'] == '미합중국인' or board_member['nationality'] == '미국인' or board_member[
                        'nationality'] == '미국':
                        board_member['nationality'] = '미국'
                    elif board_member['nationality'] == '중화인민공화국인' or board_member['nationality'] == '한국계중국인' or \
                            board_member['nationality'] == '중화인민공화':
                        board_member['nationality'] = '중국'
                    elif board_member['nationality'] == '캐나다국인' or board_member['nationality'] == '캐나다인':
                        board_member['nationality'] = '캐나다'
                    elif board_member['nationality'] == '독일국인' or board_member['nationality'] == '독일연방공화국인':
                        board_member['nationality'] = '독일'
                    elif board_member['nationality'] == '일본국인':
                        board_member['nationality'] = '일본'
                    elif board_member['nationality'] == '이란국인':
                        board_member['nationality'] = '이란'
                    elif board_member['nationality'] == '호주국인' or board_member['nationality'] == '호주' or board_member[
                        'nationality'] == '오스트레일리아국인':
                        board_member['nationality'] = '오스트레일리아'
                    elif board_member['nationality'] == '프랑스국인' or board_member['nationality'] == '블란서국인':
                        board_member['nationality'] = '프랑스'
                    elif board_member['nationality'] == '영국인':
                        board_member['nationality'] = '영국'
                    elif board_member['nationality'] == '싱가포르국인' or board_member['nationality'] == '싱가폴국인':
                        board_member['nationality'] = '싱가포르'
                    elif board_member['nationality'] == '대만국인' or board_member['nationality'] == '대만인' or board_member[
                        'nationality'] == '타이완국인' or board_member['nationality'] == '중화민':
                        board_member['nationality'] = '대만'
                    elif board_member['nationality'] == '말레이시아국인':
                        board_member['nationality'] = '말레이시아'
                    elif board_member['nationality'] == '필리핀국인':
                        board_member['nationality'] = '필리핀'
                    elif board_member['nationality'] == '뉴질랜드국인':
                        board_member['nationality'] = '뉴질랜드'
                    elif board_member['nationality'] == '스페인국인':
                        board_member['nationality'] = '스페인'
                    elif board_member['nationality'] == '이탈리아공화국인' or board_member['nationality'] == '이탈리아국인':
                        board_member['nationality'] = '이탈리아'
                    elif board_member['nationality'] == '핀란드국인':
                        board_member['nationality'] = '핀란드'
                    elif board_member['nationality'] == '인도국인' or board_member['nationality'] == '인도공화국인':
                        board_member['nationality'] = '인도'
                    elif board_member['nationality'] == '남아프리카공화국인':
                        board_member['nationality'] = '남아프리카공화국'
                    elif board_member['nationality'] == '이탈리아공화국인':
                        board_member['nationality'] == '이탈리아'
                    elif board_member['nationality'] == '스위스국인':
                        board_member['nationality'] == '스위스'
                    elif board_member['nationality'] == '아르헨티나국인':
                        board_member['nationality'] == '아르헨티나'
                    elif board_member['nationality'] == '아일랜드국인':
                        board_member['nationality'] == '아일랜드'
                    elif board_member['nationality'] == '벨기에국인':
                        board_member['nationality'] == '벨기에'
                    elif board_member['nationality'] == '네덜란드인' or board_member['nationality'] == '네덜란드국인':
                        board_member['nationality'] == '네덜란드'
                    else:
                        board_member['nationality'] = board_member['nationality'].replace('국인', '')

                    board_member['action'] = list(map(dict, collections.OrderedDict.fromkeys(
                        tuple(sorted(d.items())) for d in board_member['action'])))

                    event_sort = {'사임': 2, '사망': 2, '말소': 2, '퇴임': 2, '폐지': 2, '해임': 2, '임기만료': 2, '해산': 2,
                                    '취임': 3, '중임 및 주소기입': 3, '중임 및 주소기재': 3, '취임 및 주소기입': 3, '성명 경정': 3,
                                    '주소 경정': 3, '주소 기입': 3, '직책 경정': 3, '중임': 4, '선임':4 }
                    position_sort = {'사내이사': 2, '대표이사': 3, '공동대표이사':3}

                    board_existing_position_list = list(set([x['position'] for x in board_member['action']]))
                    for position in board_existing_position_list:
                        if position not in position_sort:
                            position_sort.update({position: 1})

                    board_existing_event_list = list(set([x['event'] for x in board_member['action']]))
                    for event in board_existing_event_list:
                        if '취임' in event:
                            event_sort.update({event: 3})
                        if ('사임') in event:
                            event_sort.update({event: 2})
                        if ('퇴임') in event:
                            event_sort.update({event: 2})
                        if ('해임') in event:
                            event_sort.update({event: 2})
                        if event not in event_sort:
                            event_sort.update({event: 1})

                    board_member['action'].sort(
                        key=lambda k: (k['date'], event_sort[k['event']], position_sort[k['position']]))




            elif key == 'share_history':
                old_data_bundles = []
                share_history_data_new = []
                for share_history_data in cor_data['share_history']:
                    if share_history_data not in old_data_bundles:
                        share_history_data_new.append(share_history_data)
                    old_data_bundles.append(share_history_data)
                cor_data['share_history'] = share_history_data_new
                cor_data['share_history'].sort(key=operator.itemgetter('date'))
                # cor_data['total_capital'] = list(map(dict, collections.OrderedDict.fromkeys(tuple(sorted(d.items())) for d in cor_data['total_capital'])))

            elif key == 'reserved_share':
                cor_data['reserved_share'] = list(map(dict, collections.OrderedDict.fromkeys(
                    tuple(sorted(d.items())) for d in cor_data['reserved_share'])))
                cor_data['reserved_share'].sort(key=operator.itemgetter('date'), reverse=True)

                cor_data['reserved_share'] = list({v['total_share']: v for v in cor_data['reserved_share']}.values())
                cor_data['reserved_share'].sort(key=operator.itemgetter('date'))

            elif key == 'share_price':
                cor_data['share_price'] = list(map(dict, collections.OrderedDict.fromkeys(
                    tuple(sorted(d.items())) for d in cor_data['share_price'])))
                cor_data['share_price'].sort(key=operator.itemgetter('date'), reverse=True)

                cor_data['share_price'] = list({v['price']: v for v in cor_data['share_price']}.values())
                cor_data['share_price'].sort(key=operator.itemgetter('date'))
            elif key == 'name':
                from itertools import groupby
                groupby_names = [list(g) for k, g in
                                 groupby(cor_data['name'], key=lambda x: (x.get('eng'), x.get('kor')))]

                name_list = []
                for idx, x in enumerate(groupby_names):
                    if idx != 0:
                        if groupby_names[idx][0]['kor'] == groupby_names[idx - 1][0]['kor']:
                            if 'eng' in groupby_names[idx][0]:
                                name_list[-1]['eng'] = groupby_names[idx][0]['eng']

                        else:
                            name_list.append(x[0])
                    else:
                        name_list.append(x[0])

                name_list = list(
                    map(dict, collections.OrderedDict.fromkeys(tuple(sorted(d.items())) for d in name_list)))

                name_list_change = []
                groupby_names = [list(g) for k, g in
                                 groupby(name_list, key=lambda x: (x.get('eng'), x.get('kor')))]

                name_list_change = []
                for idx, x in enumerate(groupby_names):
                    if idx != 0:
                        if groupby_names[idx][0]['kor'] == groupby_names[idx - 1][0]['kor']:
                            if 'eng' in groupby_names[idx][0]:
                                name_list_change[-1]['eng'] = groupby_names[idx][0]['eng']

                        else:
                            name_list_change.append(x[0])
                    else:
                        name_list_change.append(x[0])

                name_list_change = list(
                    map(dict, collections.OrderedDict.fromkeys(tuple(sorted(d.items())) for d in name_list_change)))

                cor_data['name'] = name_list_change
            elif key == 'address':
                sorted_address = sorted(cor_data['address'], key=lambda k: (k['date'], len(k['address'])))
                remove_duplicate_sorted_address = list({v['date']: v for v in sorted_address}.values())

                cor_data['address'] = remove_duplicate_sorted_address


            else:
                cor_data[key] = list(
                    map(dict, collections.OrderedDict.fromkeys(tuple(sorted(d.items())) for d in cor_data[key])))
                if key == 'status':
                    continue


                cor_data[key].sort(key=operator.itemgetter('date'))

        print('data Deduplication Complete')
        return cor_data

    def DB_Input_Request_Check(self):
        curs = self.conn_api.cursor()
        sql = 'select * from company_reg_parser where status = %s'
        curs.execute(sql, ('request',))
        request_data = curs.fetchall()

        if len(request_data):
            func_parse_now = False
            print('Currently Running')
        else:
            func_parse_now = True
            print('Not currently running')

        return func_parse_now

    def DB_Request_Data(self):
        curs = self.conn_api.cursor()
        sql = 'select corp_number from company_reg_parser where status = %s'
        curs.execute(sql, ('request',))
        request_corp_number_list = curs.fetchall()
        print('{} request corp_numbers'.format(len(request_corp_number_list)))

        return request_corp_number_list

    def DB_Input_Request(self, number):
        curs = self.conn_api.cursor()
        update_date = datetime.today().strftime("%Y-%m-%d %H:%M")

        sql = 'select * from company_reg_parser where status = %s AND corp_number = %s'
        curs.execute(sql, ('complete', number))

        complete_data = curs.fetchall()

        if len(complete_data):
            sql = 'UPDATE company_reg_parser SET status = %s, uploaded_at=%s WHERE corp_number = %s'
            curs.execute(sql, ('request', update_date, number))
            self.conn_api.commit()
            print('Change complete into request from {}'.format(number))

        else:

            curs.execute(sql, ('request', number))

            request_data = curs.fetchall()

            if len(request_data):
                pass
            else:

                sql = "INSERT INTO company_reg_parser (corp_number, status, created_at) VALUES (%s, %s, %s)"
                curs.execute(sql, (number, 'request', update_date))

                self.conn_api.commit()
                print('Insert request from {}'.format(number))

    def DB_Input_Complete(self, number):

        curs = self.conn_api.cursor()

        uploaded_date = datetime.today().strftime("%Y-%m-%d %H:%M")

        sql = 'UPDATE company_reg_parser SET status= %s, uploaded_at=%s WHERE corp_number = %s'
        curs.execute(sql, ('complete', uploaded_date, number))

        self.conn_api.commit()
        print('Update complete from {}'.format(number))
        print()

    # def DB_Company_reg_into_Company(self, corp_number,cor_data):
    #     curs = self.conn.cursor()
    #
    #     sql = """UPDATE company AS C
    #                     SET weighted_attr = %s WHERE C.corp_number=%s;"""
    #
    #     curs.execute(sql, (json.dumps(cor_data, ensure_ascii=False, indent=4), corp_number,))
    #
    #     self.conn.commit()

    def DB_Input_mismatch(self, number):

        curs = self.conn_api.cursor()

        uploaded_date = datetime.today().strftime("%Y-%m-%d %H:%M")

        sql = 'UPDATE company_reg_parser SET status= %s, uploaded_at= %s WHERE corp_number = %s'
        curs.execute(sql, ('mismatch', uploaded_date, number))

        self.conn_api.commit()
        print('Update mismatch from {}'.format(number))

    def DB_Input_Error(self, number):

        curs = self.conn_api.cursor()

        uploaded_date = datetime.today().strftime("%Y-%m-%d %H:%M")

        sql = 'UPDATE company_reg_parser SET status= %s, uploaded_at=%s WHERE corp_number = %s'
        curs.execute(sql, ('error', uploaded_date, number))

        self.conn_api.commit()
        print('Update ERROR from {}'.format(number))

    def Get_Career(self, name, birthday):

        curs = self.conn.cursor()
        sql = 'select careers from company_reg_boardmember where name = %s and dateofbirth = %s'
        curs.execute(sql, (name, birthday))
        career = curs.fetchone()
        if career != None:
            return career[0]
        else:
            return career

    def Get_one_reg_Career(self, name_birthday):

        curs = self.conn.cursor()
        placeholders = ','.join(['%s'] * len(name_birthday))
        sql = 'select careers, name, dateofbirth from company_reg_boardmember where key IN ({});'.format(placeholders)

        curs.execute(sql, name_birthday)


        career = curs.fetchall()
        return career
        # if career != None:
        #     return career
        # else:
        #     return career

    def DB_return_Json(self, cor_data):

        curs = self.conn.cursor()
        sql = 'select weighted_attr from company where corp_number = %s'

        curs.execute(sql, (cor_data['corp_number'],))
        old_db_data = curs.fetchall()
        if len(old_db_data) == 0:
            old_db_data = None
        else:
            old_db_data = old_db_data[0][0]

        if old_db_data is None or len(old_db_data)==0:
            print('Insert Json Data from %s' % cor_data['corp_number'])
            # sql = "INSERT INTO company_reg (reg_number, reg_data) VALUES (%s, %s)"
            # sql = "INSERT INTO company (corp_number, weighted_attr) VALUES (%s, %s)"
            sql = 'UPDATE company SET weighted_attr = %s WHERE corp_number = %s'

            new_update_data = self.order_duplicate_check(cor_data)
            curs.execute(sql, (
                json.dumps(cor_data, ensure_ascii=False, indent=4), cor_data['corp_number']))
        else:
            # old_db_data = old_db_data
            if cor_data['corp_number_id'][0] in old_db_data['corp_number_id']:

                if "business_type" in cor_data:
                    old_db_data['business_type'] = cor_data['business_type']
                old_db_data['announced_date'] = cor_data['announced_date']
                founded = [old_db_data['founded']] + [cor_data['founded']]
                if '0000-00-00' in founded:
                    founded.remove('0000-00-00')
                    founded = sorted(founded)
                    founded = founded + ['0000-00-00']
                old_db_data['founded'] = founded[0]
                new_update_data = Executor.update_db_json(cor_data, old_db_data)
            else:

                ####
                if type(old_db_data['corp_number_id']) == str:
                    old_db_data['corp_number_id'] = [old_db_data['corp_number_id']]

                old_db_data['corp_number_id'] = old_db_data['corp_number_id'] + cor_data['corp_number_id']

                if "business_type" in cor_data:
                    old_db_data['business_type'] = cor_data['business_type']
                old_db_data['announced_date'] = cor_data['announced_date']
                founded = [old_db_data['founded']] + [cor_data['founded']]
                if '0000-00-00' in founded:
                    founded.remove('0000-00-00')
                    founded = sorted(founded)
                    founded = founded + ['0000-00-00']
                old_db_data['founded'] = founded[0]


                new_update_data = Executor.update_db_json(cor_data, old_db_data)

        new_update_data = self.order_duplicate_check(new_update_data)
        return new_update_data

    def final(self):
        sql = "SELECT pg_terminate_backend(pid)  FROM pg_stat_activity  WHERE state ILIKE 'idl%' AND usename ILIKE ('api_company_reg%')"
        curs = self.conn.cursor()
        curs.execute(sql)
        self.conn.commit()
        self.conn.close()
        self.conn_api.close()


def parse_start(kwargs):
    #s3manager = S3Manager()
    #if mode == 'cor_numbers':
    #    keys = kwargs.getlist('cor_number')
    #elif mode == 'cor_number':
    #    keys = [kwargs['cor_number']]
    #elif mode == 'date':
    #    keys = s3manager.get_last_modified_keys(kwargs['date'])
    #    keys = [x.replace('.pdf', '') for x in keys]
    #elif mode == 'previous_version':
    #    keys = [kwargs['cor_number']]

    # logging.info("{} files will be parsed".format(len(keys)))
    # executor = Executor()
    corp_number = kwargs['cor_number'].replace('-','')
    executor_func(corp_number)

    #func_parse_now = executor.DB_Input_Request_Check()
    #for i, key in enumerate(keys):
    #    # corp_number = key.split('.')[0]
    #    key = key.replace("-", "")
    #    number = key[:6] + '-' + key[6:]
    #    executor.DB_Input_Request(number)

    #corp_number_list = executor.DB_Request_Data()

    #if mode == 'previous_version':
    #    executor_version_func(corp_number_list, func_parse_now)
    #else:
    #    executor_func(corp_number_list, func_parse_now)

    return


def executor_func(corp_number):
    print('start')
    final_start = timeit.default_timer()
    s3manager = S3Manager()
    executor = Executor()

    options = {}
    corp_number_file = corp_number + '.pdf'
    # try:
    options["pdf_path"] = corp_number_file
    # try:
    options["pdf_open"] = s3manager.get_pdf_object(options["pdf_path"])
    if len(options["pdf_open"]) == 0:
        return
    start = timeit.default_timer()
    # try:

    cor_data = executor.run(options)

    cor_data['update_date'] = date.today().strftime("%Y-%m-%d")
    # except:
    #     print('error is to parse pdf from %s ' % key)
    #     continue
    stop = timeit.default_timer()
    if cor_data['corp_number'].replace('-', '') != corp_number:
        return

    new_cor_data = executor.DB_return_Json(cor_data)
    # executor.DB_Company_reg_into_Company(cor_data['corp_number'], cor_data)



    # 등기임원 career 업데이트
    i = 0
    for b in new_cor_data['board_members']:
        new_cor_data['board_members'][i]['careers'] = executor.Get_Career(b['name'], b['birthday'])
        i = i + 1

    curs = executor.conn.cursor()
    sql = 'UPDATE company SET weighted_attr = %s WHERE corp_number = %s'
    curs.execute(sql, (
        json.dumps(new_cor_data, ensure_ascii=False, indent=4),
        new_cor_data['corp_number']))
    executor.conn.commit()


    # 등기임원 career 최신화
    sql = 'REFRESH MATERIALIZED VIEW company_reg_boardmember'
    curs = executor.conn.cursor()
    curs.execute(sql)
    executor.conn.commit()

    # 등기임원 career 업데이트
    i = 0
    for b in new_cor_data['board_members']:
        new_cor_data['board_members'][i]['careers'] = executor.Get_Career(b['name'], b['birthday'])
        i = i + 1

    sql = 'UPDATE company SET weighted_attr = %s WHERE corp_number = %s'
    curs.execute(sql, (
        json.dumps(new_cor_data, ensure_ascii=False, indent=4),
        new_cor_data['corp_number']))
    executor.conn.commit()

    namehistory_update(new_cor_data)
    address_update(new_cor_data)
    final_stop = timeit.default_timer()
    logging.info("Final WorkingTime: {} sec".format(final_stop - final_start))

    print('end')
    return


def executor_version_func(corp_number_list, func_parse_now):
    final_start = timeit.default_timer()
    s3manager = S3Manager()
    executor = Executor()
    while True:

        if func_parse_now:

            for i, key in enumerate(corp_number_list):
                # executor = Executor()
                options = {}
                corp_number = key[0].replace('-', '')
                # try:
                options["pdf_path"] = corp_number
                # try:
                pdf_opens = s3manager.get_pdf_previous_version_object(options["pdf_path"])
                pdf_opens.reverse()
                for pdf_open in pdf_opens:
                    if len(pdf_open) == 0:
                        continue
                    options["pdf_open"] = pdf_open
                    start = timeit.default_timer()
                    # try:

                    cor_data = executor.run(options)
                    cor_data['update_date'] = date.today().strftime("%Y-%m-%d")
                    # except:
                    #     print('error is to parse pdf from %s ' % key)
                    #     continue
                    stop = timeit.default_timer()
                    logging.info("WorkingTime: {} sec".format(stop - start))
                    if cor_data['corp_number'].replace('-', '') != corp_number:
                        executor.DB_Input_mismatch(corp_number[:6] + '-' + corp_number[6:])
                        continue

                    new_cor_data = executor.DB_return_Json(cor_data)
                    # executor.DB_Company_reg_into_Company(cor_data['corp_number'], cor_data)

                    # 등기임원 career 업데이트
                    i = 0
                    for b in new_cor_data['board_members']:
                        new_cor_data['board_members'][i]['careers'] = executor.Get_Career(b['name'], b['birthday'])
                        i = i + 1
                    curs = executor.conn.cursor()
                    sql = 'UPDATE company SET weighted_attr = %s WHERE corp_number = %s'
                    curs.execute(sql, (
                        json.dumps(new_cor_data, ensure_ascii=False, indent=4),
                        new_cor_data['corp_number']))
                    executor.conn.commit()

                    # 등기임원 career 최신화
                    sql = 'REFRESH MATERIALIZED VIEW company_reg_boardmember'
                    curs = executor.conn.cursor()
                    curs.execute(sql)
                    executor.conn.commit()

                    # 등기임원 career 업데이트
                    i = 0
                    for b in new_cor_data['board_members']:
                        new_cor_data['board_members'][i]['careers'] = executor.Get_Career(b['name'], b['birthday'])
                        i = i + 1

                    sql = 'UPDATE company SET weighted_attr = %s WHERE corp_number = %s'
                    curs.execute(sql, (
                        json.dumps(new_cor_data, ensure_ascii=False, indent=4),
                        new_cor_data['corp_number']))
                    executor.conn.commit()

                    executor.DB_Input_Complete(new_cor_data['corp_number'])

                final_stop = timeit.default_timer()
                logging.info("Final WorkingTime: {} sec".format(final_stop - final_start))
                corp_number_list = executor.DB_Request_Data()

                # executor.final()
                if len(corp_number_list):
                    continue
                else:
                    executor.final()
                    break
                break
            else:
                break
            break
    return 
