import urllib.request
import json
from datetime import datetime
import re
import os


def convertKORtoENGfromPapago(string):

    client_id = os.environ['client_id']  # 개발자센터에서 발급받은 Client ID 값
    client_secret = os.environ['client_secret']  # 개발자센터에서 발급받은 Client Secret 값

    encText = urllib.parse.quote(string)

    data = "source=ko&target=en&text=" + encText
    url = "https://openapi.naver.com/v1/papago/n2mt"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    try:
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    except:
        return {'error'}
    rescode = response.getcode()
    if (rescode == 200):
        response_body = response.read()
        result = json.loads(response_body.decode('utf-8'))
        return result['message']['result']['translatedText']
    else:
        print("Error Code:" + rescode)
        raise AssertionError


def convertZHtoKORfromPapago(string):
    client_id = os.environ['client_id']  # 개발자센터에서 발급받은 Client ID 값
    client_secret = os.environ['client_secret']  # 개발자센터에서 발급받은 Client Secret 값

    encText = urllib.parse.quote(string)

    data = "source=zh-TW&target=ko&text=" + encText
    url = "https://openapi.naver.com/v1/papago/n2mt"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    if (rescode == 200):
        response_body = response.read()
        result = json.loads(response_body.decode('utf-8'))
        return result['message']['result']['translatedText']
    else:
        print("Error Code:" + rescode)


def convertSpecialChar(string, to_sub):
    return re.sub(r'[\%\$\^\*\@\!\?\#\_\~\+\=\(\)\:\;\'\"\`\{\}\[\]\<\>\.\,\s\n/]', to_sub, string)

def set_name_url(string, company_id):
    name_url = None
    if string:
        if ',' in string:
            string = string.split(',')[-1]
        name_url = convertSpecialChar(string.replace(' ', '').replace('&', 'n'), '')
        from .command import Executor
        executor = Executor()
        curs = executor.conn.cursor()

        sql = 'select COUNT(*) from company where name_url ILIKE %s AND company.id != %s'
        curs.execute(sql, (name_url, company_id))
        counts = curs.fetchone()[0]
        if counts == 0:
            return name_url

        i = 1
        while counts > 0:
            sql = 'select COUNT(*) from company where name_url ILIKE %s AND company.id != %s'
            curs.execute(sql, (name_url, company_id))
            counts = curs.fetchone()[0]

            name_url = name_url.split('-')[0]
            name_url += '-{0}'.format(i)
            i += 1

    return name_url


def engClean(string):
    hangul = '[ㄱ-ㅣ가-힣]+'
    eng_name = re.sub(hangul, '', string)
    eng_name = re.sub('Incorporated|CORPORATION|Corporation|Incorporated|INCORPORATED', '', eng_name)
    eng_name = re.sub('co,|CO,|Co,', ' ', eng_name)
    eng_name = re.sub('co\.|CO\.|Co\.', ' ', eng_name)
    eng_name = re.sub(
        ',InC|,Inc|,inc|,INC|,lnc| InC| Inc| inc| INC| lnc|InC\.|Inc\.|inc\.|INC\.|lnc\.|LLC|\.Inc|\.Inc|I nc',
        '', eng_name)
    eng_name = re.sub(',Ltd|,LTD|,ltd|,INC| Ltd| LTD| ltd| INC|Ltd\.|LTD\.|ltd\.|INC\.|\.Ltd', '',
                      eng_name)
    eng_name = re.sub(' CORP| Corp| corp|\.|\,', '', eng_name).strip()

    return eng_name


def cor_data_sourceToKorEng(cor_name):
    remove_cor_type = '사회복지법인|학교법인|의료법인|사단법인|재단법인|어업회사법인|어업회사법인|농업회사 법인|농업회사|합명회사|농업회사법인|유한책임회사|주식회사|유한회사|신청|착오'

    if '구)' in cor_name['kor']:
        prefix = '구)'
    else:
        prefix = ''
    kor = cor_name['kor'].replace('구)', '').replace("株式會社", "").replace(" ", "").replace('명칭', '')
    if len(re.findall('[一-龥]', kor)):
        list_cha_ko_split = re.findall('[一-龥]+|[ㄱ-ㅣ가-힣]+', kor)
        kor = ''
        for word_ch_or_ko in list_cha_ko_split:
            if len(re.findall('[一-龥]', word_ch_or_ko)):
                try:
                    result_ch_ko = convertZHtoKORfromPapago(word_ch_or_ko)
                    kor += result_ch_ko
                except:
                    kor += ''

            else:
                kor += word_ch_or_ko

        cor_name['source'] = 'reg+papago'

    kor_clean = re.sub(remove_cor_type, '', kor).strip().replace(' ', '')

    if 'eng' in cor_name:
        eng = cor_name['eng']
    else:
        if len(kor_clean.strip()) == 0:
            cor_name['kor'] = kor_clean
            return cor_name

        else:
            eng = convertKORtoENGfromPapago(kor_clean)
            if eng != {'error'}:
                cor_name['source'] = 'reg+papago'
            else:
                eng = None
    if eng is not None:
        eng_clean = engClean(eng)
        cor_name['eng'] = eng_clean
    cor_name['kor'] = prefix + kor_clean


    return cor_name


def namehistory_dicts_extract_db(curs, company_id):
    sql_companyhistory = 'select id, date, action,detail, company_id from companyhistory where company_id = %s ORDER BY date;'

    curs.execute(sql_companyhistory, (company_id,))
    companyhistory = curs.fetchall()

    namehistory_dicts = []

    if len(companyhistory):
        modified_companyhistory = [(x[0], x[1].strftime("%Y-%m-%d"), x[2], x[3], x[4]) for x in companyhistory]

        for db_id, date, action, detail, company_id in modified_companyhistory:
            if 'kor' not in detail:
                continue
            namehistory_dict = {}
            namehistory_dict['date'] = date
            namehistory_dict['id'] = db_id
            namehistory_dict.update(detail)
            namehistory_dicts.append(namehistory_dict)

    return namehistory_dicts

def namehistory_update(cor_data):
    from .command import Executor
    executor = Executor()
    curs = executor.conn.cursor()

    created_at = datetime.today().strftime("%Y-%m-%d %H:%M")

    corp_number = cor_data['corp_number']
    cor_name_list = cor_data['name']

    for cor_name in cor_name_list:
        if 'cor_type' in cor_name:
            del cor_name['cor_type']


    sql_company_id = 'select id, city from company where corp_number = %s'
    curs.execute(sql_company_id, (corp_number,))

    fetch_result = curs.fetchone()
    if fetch_result is None:
        return True

    company_id, city = fetch_result

    if city != None:
        if '-'.join(city.split('-')[:2]) != 'CT-001':
            return True
    else:
        return True

    cor_name_list.sort(key= lambda x :x['date'], reverse=True)
    for cor_name in cor_name_list:
        if cor_name['date'] == '0000-00-00':
            continue
        from datetime import timedelta
        calc_date = datetime.strptime(cor_name['date'], "%Y-%m-%d") - timedelta(hours=9)
        cor_name['date'] = calc_date.strftime("%Y-%m-%d")

        # print(cor_name['date'], cor_name['kor'])
        # equals_kor_date_value = [x for x in namehistory_dicts if
        #                          cor_name['kor'] == x['kor'] and cor_name['date'] == x['date']]
        namehistory_dicts = namehistory_dicts_extract_db(curs, company_id)
        duplicate_namehistory = [x for x in namehistory_dicts if
                                 (cor_name['kor'] == x['kor'] and x.get('eng')) and
                                 cor_name['date'] == x['date']]
        if len(duplicate_namehistory):
            # print(cor_name['kor'],'한글 같고, 영어 있고, 날짜 같다.')
            continue

        else:
            cor_name['source'] = "reg"

            diff_date_namehistory = [x for x in namehistory_dicts if
                                     (cor_name['kor'] == x['kor'] and x.get('eng'))
                                     and cor_name['date'] != x['date']]
            if len(diff_date_namehistory):
                different_date = diff_date_namehistory[0]['date']
                cor_name_date = cor_name['date']
                diff_date = abs(
                    (datetime.strptime(cor_name_date, "%Y-%m-%d") - datetime.strptime(different_date, "%Y-%m-%d")).days)
                if diff_date <= 60:
                    # print(cor_name['kor'],'한글 같고, 영어 있고, 날짜 차이 적음.')
                    db_id = diff_date_namehistory[0]['id']
                    update_date = 'UPDATE companyhistory SET date = %s where id = %s'
                    curs.execute(update_date, (calc_date, db_id))
                else:
                    # print(cor_name['kor'],'한글 같고, 영어 있고, 날짜 차이 큼.')
                    db_id = diff_date_namehistory[0]['id']
                    db_detail = json.dumps({"eng": diff_date_namehistory[0]['eng'], "kor": diff_date_namehistory[0]['kor']}, ensure_ascii=False)
                    sql_insert = 'INSERT INTO companyhistory (date, cat, action, detail, created_at, company_id) VALUES (%s, %s, %s, %s, %s, %s)'
                    curs.execute(sql_insert, (calc_date, json.dumps(['법인'], ensure_ascii=False), '사명변경', db_detail, created_at, company_id))
                continue

            diff_name_namehistory = [x for x in namehistory_dicts if
                                     ((cor_name.get('eng') and x.get('eng') is None) or cor_name['kor'] != x['kor'])
                                     and cor_name['date'] == x['date']
                                     ]
            print('diff_name_namehistory',len(diff_name_namehistory))
            if len(diff_name_namehistory):
                # print(cor_name['kor'],'한글 다르고, 영어 있거나 없고, 날짜 같음.')
                namedicts_kor_list = [x['kor'].strip() for x in cor_name_list]
                if namedicts_kor_list.count(cor_name['kor'].strip()) >= 2:
                    continue
                cor_name = cor_data_sourceToKorEng(cor_name)
                new_cor_name = dict(cor_name)
                new_cor_name.pop('date')
                db_id = diff_name_namehistory[0]['id']
                update_date = 'UPDATE companyhistory SET detail = %s where id = %s'
                curs.execute(update_date, (json.dumps(new_cor_name, ensure_ascii=False), db_id))
                continue

            sql_insert = "INSERT INTO companyhistory (date, cat, action, detail, created_at, company_id) VALUES (%s, %s, %s, %s, %s, %s)"
            cat = json.dumps(['법인'], ensure_ascii=False)
            cor_name = cor_data_sourceToKorEng(cor_name)
            json_cor_name = {}
            if 'source' in cor_name:
                json_cor_name['source'] = cor_name['source']

            if 'eng' in cor_name:
                json_cor_name['kor'], json_cor_name['eng'], date = cor_name['kor'], cor_name['eng'], calc_date
            else:
                json_cor_name['kor'], date = cor_name['kor'], calc_date

            cor_name_dumps = json.dumps(json_cor_name, ensure_ascii=False)

            curs.execute(sql_insert, (date, cat, '사명변경', cor_name_dumps, created_at, company_id))
    executor.conn.commit()

    if len(cor_name_list) == 0:
        pass

    sql_companyhistory = 'select id, date, action, detail, company_id from companyhistory where company_id = %s and action != %s and action != %s ORDER BY date asc, created_at desc;'

    curs.execute(sql_companyhistory, (company_id,'인적분할','물적분할'))
    companyhistory = curs.fetchall()
    update_companyhistory_establish = 'UPDATE companyhistory SET action = %s where id = %s'
    delete_companyhistory_duplicate = 'DELETE from companyhistory where id = %s'

    establish_company_date = companyhistory[0][1]
    if companyhistory[0][2] != '설립':
        curs.execute(update_companyhistory_establish, ('설립', companyhistory[0][0]))

    for companyhistory_single in companyhistory[1:]:
        if companyhistory_single[1] == establish_company_date:
            curs.execute(delete_companyhistory_duplicate, (companyhistory_single[0],))
        else:
            curs.execute(update_companyhistory_establish, ('사명변경', companyhistory_single[0]))

    sql_company_name = 'select kor, eng from company where corp_number = %s'
    curs.execute(sql_company_name, (corp_number,))
    kor, eng = curs.fetchone()

    last_companyhistory = companyhistory[-1]

    # kor
    if 'kor' in last_companyhistory[3]:
        if kor != last_companyhistory[3]['kor']:
            sql_kor_update = 'UPDATE company SET kor = %s WHERE corp_number = %s'
            curs.execute(sql_kor_update, (last_companyhistory[3]['kor'], corp_number))

    if 'eng' in last_companyhistory[3]:
        if eng != last_companyhistory[3]['eng']:
            name_url = set_name_url(last_companyhistory[3]['eng'], company_id)
            sql_eng_name_url_update = 'UPDATE company SET eng = %s, name_url=%s WHERE corp_number = %s'
            curs.execute(sql_eng_name_url_update, (last_companyhistory[3]['eng'], name_url, corp_number))

    executor.conn.commit()
    print(cor_data['corp_number'], " : namehistory 완료")
    return True