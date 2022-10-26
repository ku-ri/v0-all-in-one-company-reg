from flask import Flask, request, Response
from selenium import webdriver

from APIserver.decorator import apiValidate
import time
import pyautogui
from s3manager import S3Manager
import json
import datetime
import subprocess
import shutil
from subprocess import check_output
import requests

from reg_parser.company_registration_parser.srcs.command import parse_start
import os

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine,MetaData
import re

from datetime import datetime

application = Flask(__name__)
application.debug = False
echo = True if int(os.environ['FLASK_DEBUG']) else False

APIDB_ENGINES = {
    'primary' : create_engine(
        'postgresql+psycopg2://{USER}:{PW}@{HOST}:{PORT}/{DB_NAME}'.format(**{
            'USER' : os.environ['DB_USER'],
            'PW' : os.environ['DB_PW'],
            'HOST' : os.environ['MASTER_DB_HOST'],
            'PORT' : os.environ['DB_PORT'],
            'DB_NAME' : 'apidb'
    }), logging_name='primary', echo=echo),
}


THEVCDB_ENGINES = {
    'primary' : create_engine(
        'postgresql+psycopg2://{USER}:{PW}@{HOST}:{PORT}/{DB_NAME}'.format(**{
            'USER' : os.environ['DB_USER'],
            'PW' : os.environ['DB_PW'],
            'HOST' : os.environ['MASTER_DB_HOST'],
            'PORT' : os.environ['DB_PORT'],
            'DB_NAME' : 'thevcdb'
    }), logging_name='primary', echo=echo),
}






class Connection(object):
    def __init__(self, engines):
        # echo = True if int(os.environ['FLASK_DEBUG']) else False
        self.engines = engines
        # self.engine = create_engine('postgresql+psycopg2://{0}:{1}@{2}/{3}'.format(
        #     ENV['DB_USER'], ENV['DB_PW'], ENV['DB_HOST'], db_name), echo=echo)

    # def connect(self):
    #     self.conn = self.engine.connect()
    #
    # def connectExist(self):
    #     self.Base = automap_base()
    #     self.Base.prepare(self.engine, reflect=True)

    def dispose(self):
        for k, engine in self.engines.items():
            engine.dispose()
        return

    def startSession(self, sessionRouter):
        Session = scoped_session(sessionmaker(bind=sessionRouter))
        self.session = Session()
        return



#DeclarativeBase = declarative_base()
APIDB_ENGINE = APIDB_ENGINES['primary']
#APIDB_META = MetaData(bind=APIDB_ENGINE)

THEVCDB_ENGINE = THEVCDB_ENGINES['primary']
#THEVCDB_META = MetaData(bind=THEVCDB_ENGINE)




class APIDB(Connection):
    def __init__(self):
        super(APIDB, self).__init__({
            # 'read' : APIDB_ENGINES['replica'],
            'read' : APIDB_ENGINES['primary'],
            'write' : APIDB_ENGINES['primary']
        })
        self.Base = automap_base()
        self.Base.prepare(self.engines['read'], reflect=True)

    def startSession(self):
        super(APIDB, self).startSession(APIDB_ENGINE)
        return self.session

class THEVCDB(Connection):
    def __init__(self):
        super(THEVCDB, self).__init__({
            # 'read' : APIDB_ENGINES['replica'],
            'read' : THEVCDB_ENGINES['primary'],
            'write' : THEVCDB_ENGINES['primary']
        })
        self.Base = automap_base()
        self.Base.prepare(self.engines['read'], reflect=True)

    def startSession(self):
        super(THEVCDB, self).startSession(THEVCDB_ENGINE)
        return self.session



@application.route('/company_reg/cor_number/', methods=['POST'])
def parse_single():
    parse_start(request.form, 'cor_number')

    return 'success'


def main_func():



    print('start!')
    corp_number_list = request.form.getlist('corp_number_list')



    current_time = datetime.today().strftime("%Y-%m-%d %H:%M")
    db = APIDB()
    db.startSession()
    check_table = db.Base.classes.company_reg_extract
    pre_request_now = db.session.query(check_table.corp_number).filter(check_table.status == 'request', check_table.computer == os.environ['computer']).all()
    db.session.close()
    db.dispose()

    if len(pre_request_now):
        func_extract_now = False

    else:
        func_extract_now = True


    db.startSession()

    for number in corp_number_list:
        if re.match("^\d{13}$",number.replace("-",'')) is None:
            print(number , ' : 등기번호 형식이 올바르지 않습니다')
            continue
        if len(db.session.query(check_table.corp_number).filter(check_table.corp_number == number, check_table.status == 'complete',check_table.computer == os.environ['computer']).all()):
            update_date = db.session.query(check_table).filter(check_table.corp_number == number, check_table.computer == os.environ['computer']).first()
            update_date.status = 'request'
            update_date.created_at = current_time
            db.session.commit()

            # db.session.refresh(update_date)
            # db.session.expunge(update_date)
        elif len(db.session.query(check_table.corp_number).filter(check_table.corp_number == number,
                    check_table.status == 'request', check_table.computer == os.environ['computer']).all()):
            continue

        else:
            if len(db.session.query(check_table.corp_number).filter(check_table.corp_number == number,
                                                                    check_table.status == 'complete').all()):
                update_date = db.session.query(check_table).filter(check_table.corp_number == number).first()
                update_date.status = 'request'
                update_date.created_at = current_time
                update_date.computer = os.environ['computer']
                db.session.commit()
            else:
                data_add = check_table(corp_number=number, status='request',created_at = current_time, computer=os.environ['computer'])
                db.session.add(data_add)
                db.session.commit()
    db.session.close()
    db.dispose()




    if func_extract_now:
        while True:
            db.startSession()
            request_check = db.session.query(check_table.corp_number).filter(check_table.status == 'request', check_table.computer == os.environ['computer']).all()
            db.session.close()
            db.dispose()
            if len(request_check)==0:
                break
            try:
                params = {'apikey': request.form['apikey']}
                extract_pdf_func(params)
            except Exception as e:
                time.sleep(5)
                print("error", e)
                continue
    return json.dumps('success')


@application.route('/company/pdf_extractor/', methods=['POST'])
def func():
    return Response(main_func(), mimetype='text/plain'), 201


@apiValidate
def extract_pdf_func():
    start_login = time.time()
    pyautogui.FAILSAFE = False

    # 보안프로그램 미리 설치
    params = {"user_id": os.environ['user_id'], "password": os.environ["password"]}

    #extension = 'C:/Users/thevc2/workspace/pdf_extractor/TouchEn.crx'
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_extension(extension)

    driver = webdriver.Chrome(chrome_options=chrome_options)
    #driver = webdriver.Chrome()






    #try:
    driver.get("http://www.iros.go.kr/PMainJ.jsp")




    driver.set_window_size(1920, 1080)
    driver.implicitly_wait(20)
    time.sleep(6)



    driver.find_element_by_css_selector('input#id_user_id.account_input').click()
    time.sleep(3)
    driver.find_element_by_css_selector('input#id_user_id.account_input').send_keys(params['user_id'])
    time.sleep(3)
    driver.find_element_by_css_selector('input#password').click()
    time.sleep(1)
    driver.find_element_by_css_selector('input#password').send_keys(params['password'])
    time.sleep(1)
    driver.find_element_by_css_selector('#leftS > div > form > div.id_pw > ul > li.mt05 > a').click()
    driver.implicitly_wait(30)
    time.sleep(7)


    while True:
        try:
            login_check_variable = driver.find_element_by_css_selector("#leftS > div > div.logout > p.txt").text
        except:
            login_check_variable = []
        if '좋은 하루' in login_check_variable:
            break

        try:
            driver.find_element_by_css_selector('#leftS > div > form > div.id_pw > ul > li.mt05 > a').click()
            driver.implicitly_wait(30)
            time.sleep(5)
        except Exception as e:
            if '아이디는 필수입력항목' in str(e):
                driver.switch_to.alert.accept()
                time.sleep(1)
                driver.find_element_by_css_selector('input#id_user_id.account_input').send_keys(params['user_id'])
                time.sleep(1)
                driver.find_element_by_css_selector('#leftS > div > form > div.id_pw > ul > li.mt05 > a').click()
                driver.implicitly_wait(30)
                time.sleep(5)
            elif '비밀번호는 필수입력항목' in str(e):
                driver.switch_to.alert.accept()
                time.sleep(1)
                driver.find_element_by_css_selector('input#password').send_keys(params['password'])
                driver.find_element_by_css_selector('#leftS > div > form > div.id_pw > ul > li.mt05 > a').click()
                driver.implicitly_wait(30)
                time.sleep(5)





    driver.find_element_by_css_selector('#cenS > div > ul > li:nth-child(2) > a').click()
    time.sleep(1)
    driver.find_element_by_css_selector('#cenS > div > ul > li.on > div > ul > li:nth-child(1) > a').click()
    driver.implicitly_wait(20)
    time.sleep(1)
    driver.switch_to.default_content()
    time.sleep(1)
    driver.switch_to.frame("inputFrame")
    time.sleep(1)
    driver.find_element_by_css_selector('#tab3').click()
    time.sleep(1)

    # 팝업 창 없애기
    while True:
        if len(driver.window_handles) > 1:

            driver.switch_to.window(driver.window_handles[-1])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        else:
            break
            time.sleep(1)
    # db 클래스
    db = APIDB()

    # s3manager 클래스
    s3 = S3Manager()

    print('로그인 시간 : ', str(time.time() - start_login))
    while True:

        # db 열기
        db.startSession()
        check_table = db.Base.classes.company_reg_extract

        # request 상태인 corp_number 목록 뽑기
        corp_number_list_tuple = db.session.query(check_table.corp_number).filter(check_table.status == 'request', check_table.computer == os.environ['computer']).all()
        db.session.commit()

        # db 닫기
        db.session.close()
        db.dispose()
        if len(corp_number_list_tuple)==0:
            driver.close()
            break

        corp_number_list = [x[0].strip() for x in corp_number_list_tuple if len(x)]

        for number in enumerate(corp_number_list):

            number =number[1].strip()
            print('start! ', number)
            # try:
            start = time.time()
            # 검색 후 팝업뜰 때
            try:
                driver.switch_to.default_content()
            except:
                driver.switch_to.alert.accept()
                time.sleep(1)
                driver.switch_to.default_content()
            # 등기번호 넣고 클릭
            driver.switch_to.frame("inputFrame")
            driver.find_element_by_css_selector('#SANGHO_NUM').clear()
            driver.find_element_by_css_selector('#SANGHO_NUM').send_keys(number)
            driver.find_element_by_css_selector(
                '#searchArea > form:nth-child(1) > div > div > div > div > fieldset > div > table > tbody > tr:nth-child(9) > td.btn > button').click()
            driver.implicitly_wait(10)
            time.sleep(3)

            driver.switch_to.default_content()
            driver.switch_to.frame('resultFrame')
            driver.switch_to.frame("frmOuterModal")
            # 본점 선택
            driver.find_element_by_css_selector('#distinct_ji_gb > option:nth-child(2)').click()
            # 합병/폐업 확인
            status_switch = driver.find_elements_by_css_selector('#distinct_status_cd > option')

            for idx, name in enumerate(status_switch):

                if '폐업' in name.text or '합병해산' in name.text:
                    driver.find_element_by_css_selector('#distinct_status_cd > option:nth-child(%d)' % (1 + idx)).click()
                    break
            # if driver.find_element_by_css_selector('#distinct_status_cd > option').text == '12342':
                # driver.find_element_by_css_selector('#distinct_status_cd > option:nth-child(3)').click()
            #     #살아있는 등기
            #     driver.find_element_by_css_selector('#distinct_status_cd > option:nth-child(2)').click()
            # 재검색
            driver.find_element_by_css_selector(
                'body > div > div > table:nth-child(1) > tbody > tr > td:nth-child(5) > button').click()
            driver.switch_to.default_content()
            driver.switch_to.frame("resultFrame")
            driver.switch_to.frame("frmOuterModal")


            # 주말여부 = N 클릭
            name_switch = driver.find_elements_by_css_selector(
                'body > div > div > table:nth-child(2) > tbody > tr > td:nth-child(6)')
            #name_switch.reverse()
            count = 0
            #for idx, name in enumerate(name_switch):

            thevcdb = THEVCDB()
            thevcdb.startSession()
            check_table_thevcdb = thevcdb.Base.classes.company_reg
            check_corp_number = thevcdb.session.query(check_table_thevcdb.reg_data).filter(
                check_table_thevcdb.reg_number == number).first()
            if check_corp_number:
                corp_number_id_list = check_corp_number[0]['corp_number_id']
            else:
                corp_number_id_list = []
            thevcdb.session.close()
            thevcdb.dispose()

            #index_N = [x.text for x in name_switch].index('N')

            idx_list = [idx for idx, x in enumerate(name_switch) if x.text == 'N']

            idx_list_change = idx_list[1:] + [idx_list[0]]

            index_N = idx_list_change[-1]

            #for idx in range(len(name_switch)-1,-1,-1):
            for idx in idx_list_change:

                # 처음이 아닐 때
                if count > 0:
                    # 등기번호 넣고 클릭
                    driver.switch_to.default_content()
                    driver.switch_to.frame("inputFrame")
                    driver.find_element_by_css_selector('#SANGHO_NUM').clear()
                    driver.find_element_by_css_selector('#SANGHO_NUM').send_keys(number)
                    driver.find_element_by_css_selector(
                        '#searchArea > form:nth-child(1) > div > div > div > div > fieldset > div > table > tbody > tr:nth-child(9) > td.btn > button').click()
                    driver.implicitly_wait(10)
                    time.sleep(3)

                    driver.switch_to.default_content()
                    driver.switch_to.frame('resultFrame')
                    driver.switch_to.frame("frmOuterModal")
                    # 본점 선택
                    driver.find_element_by_css_selector('#distinct_ji_gb > option:nth-child(2)').click()

                    # 재검색
                    driver.find_element_by_css_selector(
                        'body > div > div > table:nth-child(1) > tbody > tr > td:nth-child(5) > button').click()
                    driver.switch_to.default_content()
                    driver.switch_to.frame("resultFrame")
                    driver.switch_to.frame("frmOuterModal")
                    name_switch = driver.find_elements_by_css_selector(
                        'body > div > div > table:nth-child(2) > tbody > tr > td:nth-child(6)')
                corp_number_id_switch = driver.find_elements_by_css_selector("body > div > div > table:nth-child(2) > tbody > tr > td:nth-child(4)")

                name = name_switch[idx]
                corp_number_id_candidate = corp_number_id_switch[idx]



                if name.text != 'N' or (corp_number_id_candidate.text in corp_number_id_list and index_N!=idx):
                    continue

                if name.text == 'N':
                    driver.switch_to.default_content()

                    driver.switch_to.frame("resultFrame")
                    driver.switch_to.frame("frmOuterModal")
                    company_name_1 = driver.find_element_by_css_selector(
                        'body > div > div > table:nth-child(2) > tbody > tr:nth-child(%d) > td:nth-child(5) > a' % (
                                2 + idx)).text
                    driver.find_element_by_css_selector(
                        'body > div > div > table:nth-child(2) > tbody > tr:nth-child(%d) > td:nth-child(5) > a' % (
                                    2 + idx)).click()
                    count += 1
                    #break
                    driver.implicitly_wait(10)
                    time.sleep(1)


                    # 말소포함 클릭, 팝업시 확인
                    try:
                        driver.find_element_by_css_selector('#DISPLAY2').click()
                        driver.implicitly_wait(10)
                        time.sleep(1)

                        driver.find_element_by_css_selector(
                            'body > div > form > div.table_btn_bottom.margin5_b > button:nth-child(2)').click()
                    except:
                        #driver.switch_to.alert.accept()
                        try:
                            driver.switch_to.alert.accept()
                        except:
                            pass

                        driver.implicitly_wait(10)
                        time.sleep(3)

                        driver.switch_to.default_content()

                        driver.switch_to.frame("resultFrame")
                        driver.switch_to.frame("frmOuterModal")

                        driver.find_element_by_css_selector('#DISPLAY2').click()
                        driver.implicitly_wait(10)
                        time.sleep(1)

                        driver.find_element_by_css_selector(

                            'body > div > form > div.table_btn_bottom.margin5_b > button:nth-child(2)').click()
                        try:
                            driver.find_element_by_css_selector('#bchulsunchulsun5').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun6').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun7').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun8').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun9').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun10').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun11').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun12').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun13').click()
                            driver.find_element_by_css_selector('#btnNext').click()
                        except:
                            driver.find_element_by_css_selector('#bchulsunchulsun9').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun10').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun11').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun12').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun13').click()
                            driver.find_element_by_css_selector('#btnNext').click()

                    # driver.find_element_by_css_selector('#DUNCHO1').click()
                    # driver.find_element_by_css_selector(
                    #     'body > div > form > div.table_btn_bottom.margin5_b > button:nth-child(2)').click()
                    driver.implicitly_wait(10)
                    time.sleep(2)
                    driver.switch_to.default_content()
                    driver.switch_to.frame('resultFrame')
                    driver.switch_to.frame("frmOuterModal")

                    # 열람할 등기기록
                    if '열람할 등기기록' in driver.find_element_by_css_selector('h6').text:
                        driver.find_element_by_css_selector('#bchulsunchulsun14').click()
                        #driver.find_element_by_css_selector('#bchulsunchulsun15').click()
                        driver.find_element_by_css_selector('#btnNext').click()
                    try:
                        driver.switch_to.alert.accept()
                    except:
                        pass
                    # 임원항목 선택
                    driver.switch_to.default_content()
                    driver.switch_to.frame('resultFrame')
                    driver.switch_to.frame("frmOuterModal")

                    if driver.find_element_by_css_selector('h6').text == '임원항목 선택':
                        driver.find_element_by_css_selector('#bimwonsun').click()
                        time.sleep(1)
                        driver.find_element_by_css_selector('#btnNext').click()
                        driver.implicitly_wait(10)
                        time.sleep(2)

                    try:
                        # 내용이 너무 많아서 안뽑힐 때 일부만 봅기
                        alert = driver.switch_to_alert()
                        alert_text = alert.text
                        if '시스템에 과부하를 줄수있는 등기사항증명서' in alert_text:
                            driver.switch_to.alert.accept()
                            driver.implicitly_wait(10)
                            time.sleep(1)

                            driver.switch_to.default_content()

                            driver.switch_to.frame("resultFrame")
                            driver.switch_to.frame("frmOuterModal")

                            driver.find_element_by_css_selector('#DISPLAY2').click()
                            driver.find_element_by_css_selector('#DUNCHO2').click()

                            driver.implicitly_wait(10)
                            time.sleep(1)

                            driver.find_element_by_css_selector(
                                'body > div > form > div.table_btn_bottom.margin5_b > button:nth-child(2)').click()

                            driver.implicitly_wait(10)
                            time.sleep(1)

                            driver.find_element_by_css_selector('#bchulsunchulsun5').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun6').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun7').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun8').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun9').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun10').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun11').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun12').click()
                            driver.find_element_by_css_selector('#bchulsunchulsun13').click()
                            driver.find_element_by_css_selector('#btnNext').click()

                            # 임원항목 선택
                            driver.switch_to.default_content()
                            driver.switch_to.frame('resultFrame')
                            driver.switch_to.frame("frmOuterModal")

                            if driver.find_element_by_css_selector('h6').text == '임원항목 선택':
                                driver.find_element_by_css_selector('#bimwonsun').click()
                                time.sleep(1)
                                driver.find_element_by_css_selector('#btnNext').click()
                                driver.implicitly_wait(10)
                                time.sleep(2)

                    except:
                        pass


                    # 지점항목 선택
                    driver.switch_to.default_content()
                    driver.switch_to.frame('resultFrame')
                    driver.switch_to.frame("frmOuterModal")

                    if driver.find_element_by_css_selector('h6').text == '지점항목 선택':
                        time.sleep(1)
                        driver.find_element_by_css_selector('#btnNext').click()
                        driver.implicitly_wait(10)
                        time.sleep(2)
                    try:
                        driver.switch_to.alert.accept()
                    except:
                        pass
                    time.sleep(1)
                    try:
                        driver.switch_to.alert.accept()
                    except:
                        pass

                    driver.switch_to.default_content()
                    driver.switch_to.frame('resultFrame')
                    driver.switch_to.frame("frmOuterModal")

                    ### 본점, 지점 삭제
                    if '열람할 등기기록' in driver.find_element_by_css_selector('h6').text:
                        # 말소포함 클릭, 팝업시 확인
                        try:
                            driver.find_element_by_css_selector('#DISPLAY2').click()
                        except:
                            driver.switch_to.alert.accept()
                            driver.find_element_by_css_selector('#DISPLAY2').click()
                        driver.find_element_by_css_selector('#DUNCHO1').click()
                        driver.find_element_by_css_selector(
                            'body > div > form > div.table_btn_bottom.margin5_b > button:nth-child(2)').click()
                        driver.implicitly_wait(10)
                        time.sleep(1)

                        driver.switch_to.default_content()
                        driver.switch_to.frame('resultFrame')
                        driver.switch_to.frame("frmOuterModal")
                        # 열람할 등기기록
                        if '열람할 등기기록' in driver.find_element_by_css_selector('h6').text:
                            #                 driver.find_element_by_css_selector('#bchulsunchulsun14').click()
                            #                 driver.find_element_by_css_selector('#bchulsunchulsun15').click()
                            driver.find_element_by_css_selector('#btnNext').click()
                        try:
                            driver.switch_to.alert.accept()
                        except:
                            pass
                        # 임원항목 선택
                        driver.switch_to.default_content()
                        driver.switch_to.frame('resultFrame')
                        driver.switch_to.frame("frmOuterModal")

                        if driver.find_element_by_css_selector('h6').text == '임원항목 선택':
                            driver.find_element_by_css_selector('#bimwonsun').click()
                            time.sleep(1)
                            driver.find_element_by_css_selector('#btnNext').click()
                            driver.implicitly_wait(10)
                            time.sleep(4)
                    driver.implicitly_wait(10)
                    time.sleep(2)

                    try:
                        driver.switch_to.alert.accept()
                    except:
                        pass
                    time.sleep(1)
                    try:
                        driver.switch_to.alert.accept()
                    except:
                        pass

                        ###일부 - 일부만 체크
                        if '열람할 등기기록' in driver.find_element_by_css_selector('h6').text:
                            # 말소포함 클릭, 팝업시 확인
                            try:
                                driver.find_element_by_css_selector('#DISPLAY2').click()
                            except:
                                driver.switch_to.alert.accept()
                                driver.find_element_by_css_selector('#DISPLAY2').click()
                                driver.find_element_by_css_selector('#DUNCHO1').click()
                            driver.find_element_by_css_selector(
                                'body > div > form > div.table_btn_bottom.margin5_b > button:nth-child(2)').click()
                            driver.implicitly_wait(10)
                            time.sleep(1)
                            driver.switch_to.default_content()
                            driver.switch_to.frame('resultFrame')
                            driver.switch_to.frame("frmOuterModal")
                            # 열람할 등기기록
                            if '열람할 등기기록' in driver.find_element_by_css_selector('h6').text:
                                driver.find_element_by_css_selector('#bchulsunchulsun5').click()
                                driver.find_element_by_css_selector('#bchulsunchulsun6').click()
                                driver.find_element_by_css_selector('#bchulsunchulsun7').click()
                                driver.find_element_by_css_selector('#bchulsunchulsun8').click()
                                driver.find_element_by_css_selector('#bchulsunchulsun9').click()
                                driver.find_element_by_css_selector('#bchulsunchulsun10').click()
                                driver.find_element_by_css_selector('#bchulsunchulsun11').click()
                                driver.find_element_by_css_selector('#bchulsunchulsun12').click()
                                driver.find_element_by_css_selector('#bchulsunchulsun13').click()

                                driver.find_element_by_css_selector('#btnNext').click()
                            try:
                                driver.switch_to.alert.accept()
                            except:
                                pass
                            # 임원항목 선택
                            driver.switch_to.default_content()
                            driver.switch_to.frame('resultFrame')
                            driver.switch_to.frame("frmOuterModal")
                            if driver.find_element_by_css_selector('h6').text == '임원항목 선택':
                                driver.find_element_by_css_selector('#bimwonsun').click()
                                time.sleep(1)
                                driver.find_element_by_css_selector('#btnNext').click()
                                driver.implicitly_wait(10)
                                time.sleep(4)

                        driver.switch_to.default_content()
                        time.sleep(1)
                        driver.switch_to.frame('resultFrame')
                        driver.switch_to.frame("frmOuterModal")
                        if '등기신청사건' in driver.find_element_by_css_selector('body').text:
                            driver.find_element_by_css_selector(
                                'body > div > form > div.table_btn_bottom.margin5_b > button:nth-child(2)').click()
                            time.sleep(1)
                            driver.switch_to.alert.accept()

                    try:
                        # 신청사건 처리중인 등기부
                        driver.switch_to.default_content()
                        driver.switch_to.frame('resultFrame')
                        driver.switch_to.frame("frmOuterModal")


                        # 등기신청사건 처리 여부
                        if '등기신청사건 처리여부 확인' in driver.find_element_by_css_selector('strong').text:
                            driver.find_element_by_css_selector("body > div > form > div.table_btn_bottom.margin5_b > button:nth-child(2)").click()
                            time.sleep(1)
                            driver.switch_to.alert.accept()
                    except:
                        pass



                    # (주민)등록번호 공개여부 판단
                    driver.implicitly_wait(20)
                    driver.switch_to.default_content()
                    driver.switch_to.frame('resultFrame')
                    driver.switch_to.frame("frmOuterModal")
                    # driver.implicitly_wait(10)
                    time.sleep(1)


                    if driver.find_element_by_css_selector('h6').text == '(주민)등록번호 공개여부 판단':
                        driver.implicitly_wait(10)
                        time.sleep(1)
                        driver.find_element_by_css_selector('#btnNext').click()
                        driver.implicitly_wait(10)
                        time.sleep(2)

                    # 선택한 등기기록을 확인하는 화면

                    driver.switch_to.default_content()
                    driver.switch_to.frame('resultFrame')
                    driver.switch_to.frame("frmOuterModal")
                    if driver.find_element_by_css_selector('h6').text == '선택한 등기기록을 확인하는 화면입니다.':

                        driver.find_element_by_css_selector(
                            'body > form > div > div.table_btn_bottom.margin5_b > button:nth-child(2)').click()
                        driver.implicitly_wait(10)
                        time.sleep(2)
                        driver.switch_to.default_content()
                        driver.switch_to.frame("resultFrame")
                        time.sleep(2)
                        driver.find_element_by_css_selector(
                            'body > div > form:nth-child(7) > div.list_table_2line.margin5_b > table > tbody > tr > td:nth-child(4) > button').click()
                        driver.implicitly_wait(20)
                        time.sleep(4)

                        # 결제
                        payment_number1 = os.environ["payment_number1"]

                        payment_number2 = os.environ["payment_number2"]

                        payment_password = os.environ["payment_password"]

                        driver.find_element_by_css_selector("#extra3").click()
                        driver.find_element_by_css_selector('#chk_term_agree_all_emoney').click()
                        # time.sleep(1)
                        driver.find_element_by_css_selector("#inpEMoneyNo1").click()
                        time.sleep(1)
                        driver.find_element_by_css_selector("#inpEMoneyNo1").clear()
                        driver.find_element_by_css_selector("#inpEMoneyNo1").send_keys(payment_number1)

                        driver.find_element_by_css_selector("#inpEMoneyNo2").click()
                        time.sleep(1)
                        driver.find_element_by_css_selector("#inpEMoneyNo2").clear()
                        driver.find_element_by_css_selector("#inpEMoneyNo2").send_keys(payment_number2)
                        # time.sleep(1)

                        driver.find_element_by_css_selector("#inpEMoneyPswd").click()
                        time.sleep(1)
                        driver.find_element_by_css_selector("#inpEMoneyPswd").clear()
                        driver.find_element_by_css_selector("#inpEMoneyPswd").send_keys(payment_password)
                        time.sleep(1)

                        driver.find_element_by_css_selector(
                            "#EMO > div.table_btn_bottom.margin5_t > button:nth-child(1)").click()
                        driver.implicitly_wait(10)
                        time.sleep(1)

                        alert = driver.switch_to_alert()
                        alert_text = alert.text
                        if '전체 동의' in alert_text:
                            driver.switch_to.alert.accept()
                            time.sleep(1)
                            driver.find_element_by_css_selector('#chk_term_agree_all_emoney').click()
                            driver.find_element_by_css_selector(
                                "#EMO > div.table_btn_bottom.margin5_t > button:nth-child(1)").click()
                            time.sleep(1)
                        if '선불전자지급수단번호' in alert_text:
                            while True:
                                alert = driver.switch_to_alert()
                                alert_text = alert.text
                                if '선불전자지급수단번호' not in alert_text:
                                    break
                                driver.switch_to.alert.accept()
                                driver.find_element_by_css_selector("#inpEMoneyNo1").click()
                                time.sleep(5)
                                driver.find_element_by_css_selector("#inpEMoneyNo1").send_keys(payment_number1)
                                time.sleep(5)
                                driver.find_element_by_css_selector("#inpEMoneyNo2").click()
                                time.sleep(2)

                                driver.find_element_by_css_selector("#inpEMoneyNo2").send_keys(payment_number2)
                                time.sleep(5)
                                driver.find_element_by_css_selector("#inpEMoneyPswd").click()
                                time.sleep(4)

                                driver.find_element_by_css_selector(
                                    "#EMO > div.table_btn_bottom.margin5_t > button:nth-child(1)").click()
                                driver.implicitly_wait(10)
                                time.sleep(1)


                        driver.switch_to.alert.accept()

                        # 결제
                        driver.implicitly_wait(10)
                        time.sleep(2)
                        driver.find_element_by_css_selector(
                            "#snb > ul > li.on > ul > li.on > ul > li > ul > li:nth-child(3) > a").click()
                        driver.implicitly_wait(10)
                        time.sleep(2)

                        width, height = pyautogui.size()
                        pyautogui.moveTo(width / 2, height / 2)
                        pyautogui.click()
                        time.sleep(1)

                        time.sleep(3)
                        # 열람 버튼
                        driver.switch_to.default_content()
                        open_button_selector = "#Lcontent > form:nth-child(6) > div.list_table_2line > table > tbody > tr:nth-child(2) > td:nth-child(12) > button"
                        driver.find_element_by_css_selector(
                            open_button_selector).click()
                        time.sleep(2)

                        try:
                            driver.switch_to.alert.accept()
                        except:
                            pass

                    elif '중복결제' in driver.find_element_by_css_selector('h6').text:
                        # numbers.append(number)
                        # pd.DataFrame(numbers, columns=['corp_number']).to_csv('fail_list.csv', index=False)

                        driver.switch_to.default_content()
                        driver.switch_to.frame("resultFrame")
                        driver.switch_to.frame("frmOuterModal")
                        time.sleep(1)

                        #회사 이름
                        company_name_1 = driver.find_element_by_css_selector("body > div > form > div.list_table.margin5_b > table > tbody > tr:nth-child(2) > td.tx_lt").text.strip()

                        driver.find_element_by_css_selector(
                            "div.list_table.margin5_b > table > tbody > tr:nth-child(2) > td.noline_rt-tx_ct > button").click()
                        driver.implicitly_wait(10)

                        time.sleep(2)

                        driver.switch_to.default_content()
                        if '재열람' in driver.find_element_by_css_selector("#Lcontent > div.mt > h4").text:

                            stop=True
                            while stop:
                                for i in range(10):
                                    driver.implicitly_wait(10)
                                    time.sleep(4)

                                    company_name_2 = driver.find_element_by_css_selector("#Lcontent > form > div.list_table_2line > table > tbody > tr:nth-child(%d) > td:nth-child(5)" % (2 + i)).text.strip()

                                    # 열람버튼
                                    if company_name_1.count(company_name_2):

                                        #열람버튼
                                        open_button_selector = "#Lcontent > form > div.list_table_2line > table > tbody > tr:nth-child(%d) > td.noline_rt-tx_ct > button" % (2+i)
                                        driver.find_element_by_css_selector(
                                            open_button_selector).click()
                                        time.sleep(4)
                                        stop=False
                                        break
                                    if i == 9:
                                        driver.find_element_by_css_selector(
                                            "#Lcontent > form > div.pg.margin5_b > div.paginate > a.next").click()

                        # Lcontent > form > div.pg.margin5_b > div.paginate > a.next > img


                        # time.sleep(2)
                        # driver.switch_to.frame("resultFrame")
                        # # time.sleep(1)
                        # driver.switch_to.frame("frmOuterModal")
                        # time.sleep(1)
                        # 이름이 같으면

                        else:
                            for i in range(11):
                                # company_name_2 = driver.find_element_by_css_selector(
                                #     "#Lcontent > form:nth-child(6) > div.list_table_2line > table > tbody > tr:nth-child(%d) > td.tx_lt" % (
                                #                 2 + i)).text.strip()
                                # Lcontent > form:nth-child(6) > div.list_table_2line > table > tbody > tr:nth-child(2) > td.tx_lt
                                company_name_2 = driver.find_element_by_css_selector("#Lcontent > form:nth-child(6) > div.list_table_2line > table > tbody > tr:nth-child(%d) > td.tx_lt"% (2 + i)).text.strip()

                                if company_name_1.count(company_name_2):
                                    #열람버튼
                                    open_button_selector = "#Lcontent > form:nth-child(6) > div.list_table_2line > table > tbody > tr:nth-child(%d) > td:nth-child(12) > button" % (2+i)
                                    driver.find_element_by_css_selector(
                                        open_button_selector).click()
                                    time.sleep(4)
                                    break
                        try:
                            driver.switch_to.alert.accept()
                        except:
                            pass
                        try:
                            driver.switch_to.alert.accept()
                        except:
                            pass

                    # 프린트
                    try:
                        driver.switch_to.alert.accept()
                    except:
                        pass
                    time.sleep(1)
                    width, height = pyautogui.size()
                    if len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[-1])
                        driver.find_element_by_css_selector("#content1 > div.nbox > div > div > a").click()
                        time.sleep(2)
                        pyautogui.moveTo(width / 2, height / 2)
                        pyautogui.click()

                        pyautogui.press('left')
                        time.sleep(1)
                        pyautogui.press('enter')

                        driver.implicitly_wait(30)

                        time.sleep(7)



                        while True:
                            if 'iprtcrsIgmprintxctrl.xgd' in check_output("tasklist").decode('cp949').split():
                                time.sleep(1)
                                pyautogui.moveTo(width / 2, height / 2)
                                pyautogui.click()
                                time.sleep(1)
                                pyautogui.press('enter')
                            else:
                                break

                        driver.switch_to.window(driver.window_handles[0])

                        time.sleep(2)

                        driver.switch_to.default_content()
                        # driver.switch_to.frame("resultFrame")
                        # driver.switch_to.frame("frmOuterModal")
                        time.sleep(1)

                        for i in range(11):
                            # company_name_2 = driver.find_element_by_css_selector(
                            #     "#Lcontent > form:nth-child(6) > div.list_table_2line > table > tbody > tr:nth-child(%d) > td.tx_lt" % (
                            #                 2 + i)).text.strip()
                            # Lcontent > form:nth-child(6) > div.list_table_2line > table > tbody > tr:nth-child(2) > td.tx_lt
                            company_name_2 = driver.find_element_by_css_selector("#Lcontent > form:nth-child(6) > div.list_table_2line > table > tbody > tr:nth-child(%d) > td.tx_lt"% (2 + i)).text.strip()

                            if company_name_1.count(company_name_2):
                                #열람버튼
                                open_button_selector = "#Lcontent > form:nth-child(6) > div.list_table_2line > table > tbody > tr:nth-child(%d) > td:nth-child(12) > button" % (2+i)
                                driver.find_element_by_css_selector(
                                    open_button_selector).click()
                                time.sleep(4)
                                break
                        try:
                            driver.switch_to.alert.accept()
                        except:
                            pass
                        try:
                            driver.switch_to.alert.accept()
                        except:
                            pass

                    document_path = os.environ["document_path"]
                    new_file_path = os.path.join(document_path,
                                                 number.replace('-', '') + '.pdf')

                    back_up_path = os.path.join(document_path,
                                                number.replace('-', '') + '.pdf')
                    ## 폴더에 파일 있으면 지우는 코드
                    if os.path.exists(new_file_path):
                        time.sleep(3)
                        shutil.move(new_file_path, back_up_path)

                    driver.switch_to.default_content()

                    pyautogui.moveTo(width / 2, height / 2)
                    pyautogui.click()

                    pyautogui.press('left')
                    time.sleep(1)
                    pyautogui.press('enter')

                    driver.implicitly_wait(30)

                    time.sleep(6)

                    pyautogui.moveTo(width / 2, height / 2)
                    pyautogui.click()
                    pyautogui.click()
                    pyautogui.doubleClick()

                    pyautogui.press("win")
                    time.sleep(1)
                    pyautogui.press("esc")
                    time.sleep(2)

                    pyautogui.press('tab')
                    pyautogui.press('tab')
                    pyautogui.press('tab')
                    pyautogui.press('tab')
                    pyautogui.press('enter')
                    time.sleep(2)

                    pyautogui.press('enter')
                    time.sleep(10)
                    # time.sleep(3)
                    pyautogui.typewrite(str(number).replace('-', '').strip())
                    time.sleep(1)
                    pyautogui.press('enter')

                    # pyautogui.press('left')
                    time.sleep(4)
                    pyautogui.press('enter')

                    driver.implicitly_wait(20)
                    time.sleep(1)

                    pyautogui.moveTo(width / 2, height / 2)
                    pyautogui.click()


                    pyautogui.hotkey('alt','f4')
                    time.sleep(2)
                    while True:


                        if 'iprtcrsIgmprintxctrl.xgd' in check_output("tasklist").decode('cp949').split():
                            time.sleep(1)
                            pyautogui.moveTo(width / 2, height / 2)
                            pyautogui.click()
                            pyautogui.hotkey('alt','f4')
                            time.sleep(3)
                        else:
                            break


                    # pyautogui.press('tab')
                    # pyautogui.press('tab')
                    # pyautogui.press('tab')

                    # pyautogui.press('tab')
                    # pyautogui.press('tab')
                    # time.sleep(4)
                    # pyautogui.press('enter')
                    time.sleep(1)
                    new_file_path = os.path.join(document_path, number.replace('-', '') + '.pdf')
                    back_up_path =  os.path.join(document_path,"back_up", number.replace('-','') +'.pdf')
                    current_time = datetime.today().strftime("%Y-%m-%d %H:%M")
                    if os.path.exists(new_file_path):

                        s3.upload(number.replace('-','') +'.pdf',new_file_path)
                        time.sleep(3)
                        shutil.move(new_file_path,back_up_path)

                        # os.renames(new_file_path,back_up_path)
                        # time.sleep(3)
                        # os.mkdir(os.path.join('C:/', 'Users', 'thevc', 'workspace', 'file_new'))
                        db.startSession()
                        insert_data = db.session.query(check_table).filter(check_table.corp_number == number, check_table.computer == os.environ['computer']).first()
                        insert_data.status='complete'
                        insert_data.uploaded_at=current_time
                        db.session.commit()
                        db.session.close()
                        db.dispose()

                        time.sleep(2)


        #                THEVCAPIURL = os.environ['THEVC_PARSER_URL']

      #                  params = {
     #                       'apikey': THEVCAPIKEY,
    #                        'cor_number': number.replace('-','')
   #                     }
  #                      requests.post(
 #                           '%s/company_reg/cor_number/' % (THEVCAPIURL), data=params
#                        )

     #                   print(number, " request are completed")


                    try:
                        driver.switch_to.alert.accept()
                    except:
                        pass

                    driver.implicitly_wait(10)
                    time.sleep(3)
                    try:
                        driver.find_element_by_css_selector(
                            "#snb > ul > li.on > ul > li.on > ul > li > ul > li:nth-child(1) > a").click()
                    except:
                        pass
                    driver.implicitly_wait(10)

                    time.sleep(1)
                    driver.switch_to.default_content()

                    time.sleep(1)
                    driver.switch_to.frame("inputFrame")
                    driver.implicitly_wait(10)

                    time.sleep(1)
                    driver.find_element_by_css_selector('#tab3').click()

                    time.sleep(1)

                    THEVCAPIKEY = os.environ['THEVC_API_KEY']
                    params = {
                        'apikey': THEVCAPIKEY,
                        'cor_number': number.replace('-', '')
                    }

                    parse_start(params)





            db.startSession()
            insert_data = db.session.query(check_table).filter(check_table.corp_number == number, check_table.computer == os.environ['computer']).first()
            insert_data.status = 'complete'
            insert_data.uploaded_at = current_time
            db.session.commit()
            db.session.close()
            db.dispose()
            sec = time.time() - start

            print(number, ", 실행시간 : ", sec)

            print()

    #except Exception as e:
     #   if 'http://www.iros.go.kr/XecureObject/installAnySign.jsp' in driver.current_url:
      #      subprocess.Popen("TouchEn_nxKey_Installer.exe")
       #     time.sleep(2)
        #    pyautogui.press('enter')
         #   time.sleep(13)
          #  pyautogui.press('enter')
        #raise











if __name__ == '__main__':
    if not application.debug:
        application.run(host='0.0.0.0', port=80)
    else:
        application.run(host='127.0.0.1', port=8888)

# run run run away
