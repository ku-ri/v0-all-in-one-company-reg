# -*- coding: utf-8 -*-


import re


class Board_Members_Extractor:
    open_date_re = re.compile("\d{4}년\d{2}월\d{2}일")

    board_foreign_eng_name_re = re.compile('\(.+\)')
    board_member_re = re.compile('\d{6}-\*{7}')

    board_member_date_re = re.compile('\d{4} 년  \d{2} 월  \d{2} 일|년     월     일|\d{4}\.\d{1,2}\.\d{1,2}\.생|\d{1}.*년.*월.*일')
    board_foreign_date_re = re.compile('\d{4}년 \d{1,2}월 \d{1,2}일생|\d{4}\.\d{1,2}\.\d{1,2}\.생')
    board_foreign_date_re2 = re.compile('\d{4}\.\d{1,2}\.\d{1,2}\.생')
    board_foreign_date_re3 = re.compile('\d{4}년 \d{1,2}월 \d{1,2}일생')


    def __init__(self, idx, pdf_list, founded):
        self.founded = founded

        self.board_members_list = self.board_members_coverage_extractor(idx, pdf_list, len(pdf_list))

    def board_members_extractor(self):
        name_error = None
        nationality_error = None
        birthday_error = None
        positions = list()
        event_dict = list()
        person_dict = dict()
        event_dicts = list()
        person_dicts = list()
        event_dict_dicts = list()
        board_candidates = list()
        count = 0
        new = False
        position = ""
        event_skip = False
        for board_idx, board_candidate in enumerate(self.board_members_list):
            if len(board_candidate.split()) > 2:
                if '******' in board_candidate.split()[2] or self.board_foreign_date_re.search(board_candidate):
                    try:
                        event_skip = False
                        count += 1
                        new = True
                        position = board_candidate.split()[0].strip()

                        # if self.board_foreign_date_re.search(board_candidate):
                        if '국인' in board_candidate or board_candidate.split()[1]=='미국' \
                                or board_candidate.split()[1]=='캐나다인' or board_candidate.split()[1]=='호주' \
                                or board_candidate.split()[1]=='대만인' or board_candidate.split()[1]=='네덜란드인' \
                                or board_candidate.split()[1]=='중화인민공화':
                            nationality_raw = board_candidate.split()[1]
                            if nationality_raw=='미합중국인' or nationality_raw=='미국인' or nationality_raw=='미국':
                                nationality = '미국'
                            elif nationality_raw=='중화인민공화국인' or nationality_raw=='한국계중국인' or nationality_raw=='중화인민공화':
                                nationality = '중국'
                            elif nationality_raw=='캐나다국인' or nationality_raw=='캐나다인':
                                nationality = '캐나다'
                            elif nationality_raw=='독일국인' or nationality_raw=='독일연방공화국인':
                                nationality = '독일'
                            elif nationality_raw=='일본국인':
                                nationality = '일본'
                            elif nationality_raw=='이란국인':
                                nationality = '이란'
                            elif nationality_raw=='호주국인' or nationality_raw=='호주':
                                nationality = '오스트레일리아'
                            elif nationality_raw=='프랑스국인' or nationality_raw=='블란서국인':
                                nationality = '프랑스'
                            elif nationality_raw=='영국인':
                                nationality = '영국'
                            elif nationality_raw=='싱가포르국인' or nationality_raw=='싱가폴국인':
                                nationality = '싱가포르'
                            elif nationality_raw=='대만국인' or nationality_raw=='대만인' or nationality_raw=='타이완국인':
                                nationality = '대만'
                            elif nationality_raw=='말레이시아국인':
                                nationality = '말레이시아'
                            elif nationality_raw=='필리핀국인':
                                nationality = '필리핀'
                            elif nationality_raw=='뉴질랜드국인':
                                nationality = '뉴질랜드'
                            elif nationality_raw=='스페인국인':
                                nationality = '스페인'
                            elif nationality_raw=='이탈리아공화국인':
                                nationality = '이탈리아'
                            elif nationality_raw=='핀란드국인':
                                nationality = '핀란드'
                            elif nationality_raw=='인도국인' or nationality_raw=='인도공화국인':
                                nationality = '인도'
                            elif nationality_raw=='남아프리카공화국인':
                                nationality = '남아프리카공화국'
                            elif nationality_raw=='이탈리아공화국인':
                                nationality == '이탈리아'
                            elif nationality_raw =='네덜란드인':
                                nationality == '네덜란드'
                            else:
                                nationality = nationality_raw.replace('국인','')


                            if len(board_candidate.split()[2]) > 45:
                                name='error'
                                name_error = True
                                nationality_error = True
                                continue



                            if self.board_foreign_eng_name_re.search(board_candidate):
                                board_candidate_eng_name = self.board_foreign_eng_name_re.findall(board_candidate)
                                board_candidate = re.sub(self.board_foreign_eng_name_re, '', board_candidate)
                                name = board_candidate.split()[2]
                                eng_name = board_candidate_eng_name[0].replace('(', '').replace(')', '')
                                person_dict["eng"] = eng_name
                            else:
                                name = board_candidate.split()[2]
                            if self.board_foreign_date_re2.search(board_candidate):
                                birthday = self.board_foreign_date_re2.findall(board_candidate)[0].replace('생',
                                                                                                           '.').replace('.',
                                                                                                                        '-')[:-2]
                                if len(birthday.split('-')[1]) == 1:
                                    birthday = birthday.split('-')[0] +'-'+ '0' + birthday.split('-')[1] +'-'+ birthday.split('-')[2]
                                if len(birthday.split('-')[2]) == 1:
                                    birthday = birthday.split('-')[0]+'-'+ birthday.split('-')[1] +'-'+ '0' + birthday.split('-')[2]


                            else:
                                registration_number = self.board_foreign_date_re.findall(board_candidate)[0].replace(' ',
                                                                                                                     '')
                                year = registration_number.split('년')[0].strip()
                                month = registration_number.split('년')[1].split('월')[0].strip()
                                if len(month) == 1:
                                    month = '0' + month
                                day = registration_number.split('년')[1].split('월')[1].split('일생')[0].strip()
                                if len(day) == 1:
                                    day = '0' + day
                                birthday = '%s-%s-%s' % (year, month, day)
                        else:
                            nationality = '한국'
                            name = board_candidate.split()[1].strip()
                            if self.board_foreign_date_re2.search(board_candidate):
                                birthday = self.board_foreign_date_re2.findall(board_candidate)[0].replace('생', '.').replace(
                                    '.',
                                    '-')[:-2]
                                if len(birthday.split('-')[1])==1:
                                    birthday = birthday.split('-')[0] +'-'+'0' + birthday.split('-')[1] +'-'+ birthday.split('-')[2]
                                if len(birthday.split('-')[2])==1:
                                    birthday = birthday.split('-')[0] +'-'+  birthday.split('-')[1] +'-'+ '0' + birthday.split('-')[2]

                            elif self.board_foreign_date_re3.search(board_candidate):
                                registration_number = self.board_foreign_date_re3.findall(board_candidate)[0].replace(' ',
                                                                                                                     '')
                                year = registration_number.split('년')[0].strip()
                                month = registration_number.split('년')[1].split('월')[0].strip()
                                if len(month) == 1:
                                    month = '0' + month
                                day = registration_number.split('년')[1].split('월')[1].split('일생')[0].strip()
                                if len(day) == 1:
                                    day = '0' + day
                                birthday = '%s-%s-%s' % (year, month, day)
                            else:
                                registration_number = board_candidate.split()[2]

                                if registration_number[0] == '0' or registration_number[0] == '1':
                                    birthday = '20%s-%s-%s' % (
                                        registration_number[:2], registration_number[2:4], registration_number[4:6])
                                else:
                                    birthday = '19%s-%s-%s' % (
                                        registration_number[:2], registration_number[2:4], registration_number[4:6])


                        if count > 2:
                            old_board_candidates = board_candidates[-1].split()
                            new_board_candidate = board_candidate.split()
                            if old_board_candidates[1] == new_board_candidate[1] and old_board_candidates[2] == new_board_candidate[2]:
                                new = False
                                continue
                        if re.match('[0-9]+', name):
                            name = 'error'
                            name_error = True
                            # raise NotImplementedError
                        if re.match('[0-9]+', nationality):
                            nationality = 'error'
                            nationality_error = True
                            # raise NotImplementedError

                        if re.match('\d{4}-\d{2}-\d{2}', birthday) is None:
                            # birthday = 'error'
                            birthday_error = True
                            # raise NotImplementedError

                        board_candidates.append(board_candidate)
                        person_dict["birthday"] = birthday.strip()
                        person_dict["name"] = name
                        person_dict["nationality"] = nationality
                        positions.append(position)
                        person_dicts.append(person_dict)
                        person_dict = {}
                    except:
                        person_dict["birthday"] = 'error'
                        person_dict["name"] = 'error'
                        person_dict["nationality"] = 'error'
                        positions.append(position)
                        person_dicts.append(person_dict)
                        person_dict = {}
                        event_skip = True



                elif self.board_member_date_re.search(board_candidate):
                    if event_skip:
                        continue
                    board_candidates.append(board_candidate)


                    # board_candidate = board_candidate.strip().split('   ')[0]
                    board_date_two = self.board_member_date_re.findall(board_candidate)
                    if len(board_date_two)!=2:
                        continue
                    board_patten1 = board_date_two[0]

                    board_patten2 = board_candidate.split(board_date_two[0])[1].split(board_date_two[1])[0]

                    event = board_patten2.strip()
                    if board_patten1=='년     월     일':
                        if len(event_dict_dicts) and len(event_dict_dicts[-1]):
                            date = event_dict_dicts[-1][-1]['date']
                        else:
                            date = self.founded
                    else:
                        date = board_patten1.replace(' 년  ', '-').replace(' 월  ', '-').replace(' 일', '').strip()
                    event_dict = {"position": position, "event": event,
                                   "date": date}
                    if len(event_dict):
                        event_dicts.append(event_dict)
                        event_dict = []
                else:
                    continue


                if new:
                    if count > 1:
                        new = False
                        event_dict_dicts.append(event_dicts)
                        event_dicts = []

        event_dict_dicts.append(event_dicts)

        person_dict_finals = list()
        birthdays = list()
        names = list()
        for person_dict_idx, (event_dict_candidate, person_dict_candidate) in enumerate(
                zip(event_dict_dicts, person_dicts)):
            if len(event_dict_candidate) == 0:
                event_dict_candidate = [
                    {"position": positions[person_dict_idx], "event": '취임', "date": self.founded}]
            birthday = person_dict_candidate["birthday"]
            name = person_dict_candidate["name"]

            if birthday not in birthdays or name not in names:
                person_dict_candidate["action"] = event_dict_candidate
                person_dict_finals.append(person_dict_candidate)
            else:
                for person_dict_idx, person_history in enumerate(person_dict_finals):
                    if person_history["birthday"] == birthday:
                        person_dict_finals[person_dict_idx]["action"] = person_dict_finals[person_dict_idx][
                                                                            "action"] + event_dict_candidate
                        break
            birthdays.append(birthday)
            names.append(name)

        return person_dict_finals, name_error, nationality_error,birthday_error

    def board_members_coverage_extractor(self, idx, pdf_list, length):

        idx_list = list()
        idx_list.append(idx + 1)

        while idx <= length - 2:
            idx = idx + 1
            if len(self.board_member_re.findall(pdf_list[idx])) + len(
                    self.board_foreign_date_re.findall(pdf_list[idx])):
                idx_list.append(idx)
        return pdf_list[idx_list[0]:idx_list[-1] + 4]


class Board_Members_Staff_Extractor:
    open_date_re = re.compile("\d{4}년\d{2}월\d{2}일")

    board_foreign_eng_name_re = re.compile('\(.+\)')
    board_member_re = re.compile('\d{6}-\*{7}')

    board_member_date_re = re.compile('\d{4} 년  \d{2} 월  \d{2} 일|년     월     일|\d{4}\.\d{1,2}\.\d{1,2}\.생')
    board_foreign_date_re = re.compile('\d{4}년 \d{1,2}월 \d{1,2}일생|\d{4}\.\d{1,2}\.\d{1,2}\.생')
    board_foreign_date_re2 = re.compile('\d{4}\.\d{1,2}\.\d{1,2}\.생')
    board_foreign_date_re3 = re.compile('\d{4}년 \d{1,2}월 \d{1,2}일생')

    board_exec_re = re.compile('전부이행')

    def __init__(self, idx, pdf_list, founded):
        self.founded = founded

        self.board_members_list = self.board_members_coverage_extractor(idx, pdf_list, len(pdf_list))

    def board_members_extractor(self):
        name_error = None
        nationality_error = None
        birthday_error = None
        positions = list()
        event_dict = list()
        person_dict = dict()
        event_dicts = list()
        person_dicts = list()
        event_dict_dicts = list()
        board_candidates = list()
        count = 0
        new = False
        position = ""
        event_skip = False
        for board_idx, board_candidate in enumerate(self.board_members_list):
            if len(board_candidate.split()) > 2:
                if '******' in board_candidate.split()[2] or self.board_foreign_date_re.search(board_candidate):
                    try:
                        event_skip = False
                        count += 1
                        new = True
                        position = board_candidate.split()[0].strip()

                        # if self.board_foreign_date_re.search(board_candidate):
                        if '국인' in board_candidate or board_candidate.split()[1] == '미국' \
                                or board_candidate.split()[1] == '캐나다인' or board_candidate.split()[1] == '호주' \
                                or board_candidate.split()[1] == '대만인' or board_candidate.split()[1] == '네덜란드인' \
                                or board_candidate.split()[1] == '중화인민공화':
                            nationality_raw = board_candidate.split()[1]
                            if nationality_raw == '미합중국인' or nationality_raw == '미국인' or nationality_raw == '미국':
                                nationality = '미국'
                            elif nationality_raw == '중화인민공화국인' or nationality_raw == '한국계중국인' or nationality_raw == '중화인민공화':
                                nationality = '중국'
                            elif nationality_raw == '캐나다국인' or nationality_raw == '캐나다인':
                                nationality = '캐나다'
                            elif nationality_raw == '독일국인' or nationality_raw == '독일연방공화국인':
                                nationality = '독일'
                            elif nationality_raw == '일본국인':
                                nationality = '일본'
                            elif nationality_raw == '이란국인':
                                nationality = '이란'
                            elif nationality_raw == '호주국인' or nationality_raw == '호주':
                                nationality = '오스트레일리아'
                            elif nationality_raw == '프랑스국인' or nationality_raw == '블란서국인':
                                nationality = '프랑스'
                            elif nationality_raw == '영국인':
                                nationality = '영국'
                            elif nationality_raw == '싱가포르국인' or nationality_raw == '싱가폴국인':
                                nationality = '싱가포르'
                            elif nationality_raw == '대만국인' or nationality_raw == '대만인' or nationality_raw == '타이완국인':
                                nationality = '대만'
                            elif nationality_raw == '말레이시아국인':
                                nationality = '말레이시아'
                            elif nationality_raw == '필리핀국인':
                                nationality = '필리핀'
                            elif nationality_raw == '뉴질랜드국인':
                                nationality = '뉴질랜드'
                            elif nationality_raw == '스페인국인':
                                nationality = '스페인'
                            elif nationality_raw == '이탈리아공화국인':
                                nationality = '이탈리아'
                            elif nationality_raw == '핀란드국인':
                                nationality = '핀란드'
                            elif nationality_raw == '인도국인' or nationality_raw == '인도공화국인':
                                nationality = '인도'
                            elif nationality_raw == '남아프리카공화국인':
                                nationality = '남아프리카공화국'
                            elif nationality_raw == '이탈리아공화국인':
                                nationality == '이탈리아'
                            elif nationality_raw == '네덜란드인':
                                nationality == '네덜란드'
                            else:
                                nationality = nationality_raw.replace('국인', '')

                            if len(board_candidate.split()[2]) > 45:
                                name = 'error'
                                name_error = True
                                nationality_error = True
                                continue

                            if self.board_foreign_eng_name_re.search(board_candidate):
                                board_candidate_eng_name = self.board_foreign_eng_name_re.findall(board_candidate)
                                board_candidate = re.sub(self.board_foreign_eng_name_re, '', board_candidate)
                                name = board_candidate.split()[2]
                                eng_name = board_candidate_eng_name[0].replace('(', '').replace(')', '')
                                person_dict["eng"] = eng_name
                            else:
                                name = board_candidate.split()[2]
                            if self.board_foreign_date_re2.search(board_candidate):
                                birthday = self.board_foreign_date_re2.findall(board_candidate)[0].replace('생',
                                                                                                           '.').replace(
                                    '.',
                                    '-')[:-2]
                                if len(birthday.split('-')[1]) == 1:
                                    birthday = birthday.split('-')[0] + '-' + '0' + birthday.split('-')[1] + '-' + \
                                               birthday.split('-')[2]
                                if len(birthday.split('-')[2]) == 1:
                                    birthday = birthday.split('-')[0] + '-' + birthday.split('-')[1] + '-' + '0' + \
                                               birthday.split('-')[2]


                            else:
                                registration_number = self.board_foreign_date_re.findall(board_candidate)[0].replace(
                                    ' ',
                                    '')
                                year = registration_number.split('년')[0].strip()
                                month = registration_number.split('년')[1].split('월')[0].strip()
                                if len(month) == 1:
                                    month = '0' + month
                                day = registration_number.split('년')[1].split('월')[1].split('일생')[0].strip()
                                if len(day) == 1:
                                    day = '0' + day
                                birthday = '%s-%s-%s' % (year, month, day)
                        else:
                            nationality = '한국'
                            name = board_candidate.split()[1].strip()
                            if self.board_foreign_date_re2.search(board_candidate):
                                birthday = self.board_foreign_date_re2.findall(board_candidate)[0].replace('생',
                                                                                                           '.').replace(
                                    '.',
                                    '-')[:-2]
                                if len(birthday.split('-')[1]) == 1:
                                    birthday = birthday.split('-')[0] + '-' + '0' + birthday.split('-')[1] + '-' + \
                                               birthday.split('-')[2]
                                if len(birthday.split('-')[2]) == 1:
                                    birthday = birthday.split('-')[0] + '-' + birthday.split('-')[1] + '-' + '0' + \
                                               birthday.split('-')[2]

                            elif self.board_foreign_date_re3.search(board_candidate):
                                registration_number = self.board_foreign_date_re3.findall(board_candidate)[0].replace(
                                    ' ',
                                    '')
                                year = registration_number.split('년')[0].strip()
                                month = registration_number.split('년')[1].split('월')[0].strip()
                                if len(month) == 1:
                                    month = '0' + month
                                day = registration_number.split('년')[1].split('월')[1].split('일생')[0].strip()
                                if len(day) == 1:
                                    day = '0' + day
                                birthday = '%s-%s-%s' % (year, month, day)
                            else:
                                registration_number = board_candidate.split()[2]

                                if registration_number[0] == '0' or registration_number[0] == '1':
                                    birthday = '20%s-%s-%s' % (
                                        registration_number[:2], registration_number[2:4], registration_number[4:6])
                                else:
                                    birthday = '19%s-%s-%s' % (
                                        registration_number[:2], registration_number[2:4], registration_number[4:6])

                        if count > 2:
                            old_board_candidates = board_candidates[-1].split()
                            new_board_candidate = board_candidate.split()
                            if old_board_candidates[1] == new_board_candidate[1] and old_board_candidates[2] == \
                                    new_board_candidate[2]:
                                new = False
                                continue
                        if re.match('[0-9]+', name):
                            name = 'error'
                            name_error = True
                            # raise NotImplementedError
                        if re.match('[0-9]+', nationality):
                            nationality = 'error'
                            nationality_error = True
                            # raise NotImplementedError

                        if re.match('\d{4}-\d{2}-\d{2}', birthday) is None:
                            # birthday = 'error'
                            birthday_error = True
                            # raise NotImplementedError

                        board_candidates.append(board_candidate)
                        person_dict["birthday"] = birthday.strip()
                        person_dict["name"] = name
                        person_dict["nationality"] = nationality
                        positions.append(position)
                        person_dicts.append(person_dict)
                        person_dict = {}
                    except:
                        person_dict["birthday"] = 'error'
                        person_dict["name"] = 'error'
                        person_dict["nationality"] = 'error'
                        positions.append(position)
                        person_dicts.append(person_dict)
                        person_dict = {}
                        event_skip = True



                elif self.board_member_date_re.search(board_candidate):
                    if event_skip:
                        continue
                    board_candidates.append(board_candidate)

                    # board_candidate = board_candidate.strip().split('   ')[0]
                    #                     board_date_two = self.board_member_date_re.findall(board_candidate)
                    #                     if len(board_date_two)!=2:
                    #                         continue
                    #                     board_patten1 = board_date_two[0]

                    #                     board_patten2 = board_candidate.split(board_date_two[0])[1].split(board_date_two[1])[0]

                    #                     event = board_patten2.strip()
                    #                     if board_patten1=='년     월     일':
                    #                         if len(event_dict_dicts) and len(event_dict_dicts[-1]):
                    #                             date = event_dict_dicts[-1][-1]['date']
                    #                         else:
                    #                             date = self.founded
                    #                     else:
                    #                         date = board_patten1.replace(' 년  ', '-').replace(' 월  ', '-').replace(' 일', '').strip()
                    event_dict = {"position": position, "event": '취임',
                                  "date": self.founded}
                    if len(event_dict):
                        event_dicts.append(event_dict)
                        event_dict = []
                else:
                    continue

                if new:
                    if count > 1:
                        new = False
                        event_dict_dicts.append(event_dicts)
                        event_dicts = []

        event_dict_dicts.append(event_dicts)

        person_dict_finals = list()
        birthdays = list()
        names = list()
        for person_dict_idx, (event_dict_candidate, person_dict_candidate) in enumerate(
                zip(event_dict_dicts, person_dicts)):
            if len(event_dict_candidate) == 0:
                event_dict_candidate = [
                    {"position": positions[person_dict_idx], "event": '취임', "date": self.founded}]
            birthday = person_dict_candidate["birthday"]
            name = person_dict_candidate["name"]

            if birthday not in birthdays or name not in names:
                person_dict_candidate["action"] = event_dict_candidate
                person_dict_finals.append(person_dict_candidate)
            else:
                for person_dict_idx, person_history in enumerate(person_dict_finals):
                    if person_history["birthday"] == birthday:
                        person_dict_finals[person_dict_idx]["action"] = person_dict_finals[person_dict_idx][
                                                                            "action"] + event_dict_candidate
                        break
            birthdays.append(birthday)
            names.append(name)

        return person_dict_finals, name_error, nationality_error, birthday_error

    def board_members_coverage_extractor(self, idx, pdf_list, length):

        idx_list = list()
        idx_list.append(idx + 1)

        while idx <= length - 2:
            idx = idx + 1
            if len(self.board_member_re.findall(pdf_list[idx])) + len(
                    self.board_foreign_date_re.findall(pdf_list[idx])):
                idx_list.append(idx)
        return pdf_list[idx_list[0]:idx_list[-1] + 4]