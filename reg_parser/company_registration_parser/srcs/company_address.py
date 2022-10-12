import os
import json
import requests
import re


def getCode(data, cat):
    from .command import Executor
    executor = Executor()
    sql_classification = 'select code from classification where cat = %s and kor = %s'
    curs = executor.conn.cursor()
    curs.execute(sql_classification, (cat, data))
    fetch_result = curs.fetchone()
    if fetch_result:
        return fetch_result[0]


def getGeoCode(address):
    geoCode = []
    if address:
        url = 'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode'
        params = {
            'query': address
        }
        headers = {
            'X-NCP-APIGW-API-KEY-ID': os.environ['NCP_API_KEY_ID'],
            'X-NCP-APIGW-API-KEY': os.environ['NCP_API_KEY']
        }
        result = json.loads(requests.get(url, params=params, headers=headers).text)
        if 'addresses' in result:
            if len(result['addresses']) > 0:
                location = [float(result['addresses'][0]['y']), float(result['addresses'][0]['x'])]
                state = str(result['addresses'][0]['addressElements'][0]['longName'])
                search = re.search(r'.*(도)', state)
                if search:
                    city = str(result['addresses'][0]['addressElements'][1]['longName']).split(' ')[0]
                else:
                    city = str(result['addresses'][0]['addressElements'][0]['longName'])

                if city != None:
                    city_code = getCode(city, '도시')
                    state_code = '-'.join(city_code.split('-')[:3]).replace("CT", "ST")
                else:
                    state_code = None
                    city_code = None
                return {'location': location, 'state': state_code, 'city': city_code}
    return geoCode


def address_update(cor_data):
    from .command import Executor
    executor = Executor()
    curs = executor.conn.cursor()
    corp_number = cor_data['corp_number']
    cor_address = cor_data['address']

    sorted_cor_address = sorted(cor_address, key=lambda k: k['date'])

    if len(sorted_cor_address) == 0:
        return True
    last_address = sorted_cor_address[-1]

    sql_company_address = 'select address, city from company where corp_number = %s'
    curs.execute(sql_company_address, (corp_number,))

    fetch_result = curs.fetchone()
    if fetch_result is None:
        return True

    company_address, city = fetch_result
    if city != None:
        if '-'.join(city.split('-')[:2]) != 'CT-001':
            return True
    else:
        return True

    if company_address is None:
        return True

    current_address = company_address.strip()
    reg_address = last_address['address'].strip()

    if current_address.replace(' ', '') != reg_address.replace(' ', ''):
        geoCode = getGeoCode(reg_address)
        if len(geoCode) > 0:
            print('current_address', current_address)
            executor = Executor()
            curs = executor.conn.cursor()
            if geoCode['city']:
                sql_update_address_location = 'UPDATE company SET state = %s, city = %s, address = %s, location = %s WHERE corp_number = %s'
                curs.execute(sql_update_address_location, (
                geoCode['state'], geoCode['city'], reg_address, json.dumps(geoCode['location']), corp_number))
                print('reg_address', geoCode['state'], geoCode['city'], reg_address)
            else:
                sql_update_address_location = 'UPDATE company SET address = %s, location = %s WHERE corp_number = %s'
                curs.execute(sql_update_address_location, (reg_address, json.dumps(geoCode['location']), corp_number))
                print('reg_address', reg_address)
            executor.conn.commit()
            print(cor_data['corp_number'], "address 변경 완료")
    return True