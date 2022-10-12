from company_registration_parser.srcs.command import Executor
import json
import time

def main():

    executor = Executor()

    curs = executor.conn.cursor()
    sql = 'select corp_number from company'

    curs.execute(sql)
    corp_numbers_all_tuple = curs.fetchall()

    corp_numbers_all = [x[0] for x in corp_numbers_all_tuple if x[0] is not None]

    # 등기임원 career 최신화
    sql = 'REFRESH MATERIALIZED VIEW company_reg_boardmember'
    curs.execute(sql)
    executor.conn.commit()

    for corp_number in corp_numbers_all:

        sql = 'select weighted_attr from company where corp_number = %s'
        curs.execute(sql, (corp_number,))
        cor_data = curs.fetchone()
        if cor_data is None:
            continue
        cor_data = cor_data[0]
        if cor_data is None:
            continue



        # 등기임원 career 업데이트
        if 'board_members' in cor_data:
            name_birthday = [x['name']+x['birthday'] for x in cor_data['board_members']]
            # cor_data['board_members'][i]['careers'] = executor.Get_one_reg_Career(name_birthday)
            name_birthday_career = executor.Get_one_reg_Career(name_birthday)
            for careers, name, dateofbirth in name_birthday_career:
                for idx, b in enumerate(cor_data['board_members']):
                    if b['name'] == name and b['birthday'] == dateofbirth:
                        cor_data['board_members'][idx]['careers'] = careers



        sql = 'UPDATE company SET weighted_attr = %s WHERE corp_number = %s'

        curs.execute(sql, (
            json.dumps(cor_data, ensure_ascii=False, indent=4),
            corp_number))

        print(corp_number, " : 완료")
    executor.conn.commit()
    executor.final()
    return


if __name__ == '__main__':
    start = time.time()
    main()
    print(time.time()-start)