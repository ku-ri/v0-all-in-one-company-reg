from flask import Flask, request
import os

#import smtplib
#gfrom email.mime.text import MIMEText


from company_registration_parser.srcs.command import parse_start


application = Flask(__name__)
application.debug = True


#ADMINS = [os.environ['ADMIN_EMAIL'].split('/')[0]]
#if not application.debug:
#    import logging
 #   from logging.handlers import SMTPHandler
  #  mail_handler = SMTPHandler(
   #     mailhost=(os.environ['EMAIL_HOST'], os.environ['EMAIL_PORT']),
    #    fromaddr=os.environ['EMAIL_HOST_USER'],
     #   toaddrs=ADMINS, subject='[API SERVER by Flask] YourApplication Failed',
     #   credentials=(os.environ['EMAIL_HOST_USER'], os.environ['EMAIL_HOST_PASSWORD']),
      #  secure=())
    #mail_handler.setLevel(logging.ERROR)
    #application.logger.addHandler(mail_handler)

#def read_last_lines(filename, no_of_lines=1):
#    file = open(filename,'r')
#    lines = file.readlines()
#    last_lines = lines[-no_of_lines:]
#    file.close()
#    smtp = smtplib.SMTP(os.environ['EMAIL_HOST'], os.environ['EMAIL_PORT'])
#    smtp.starttls()
#    smtp.login(os.environ['EMAIL_HOST_USER'], os.environ['EMAIL_APP_PASSWORD'])
#    msg = MIMEText('  '.join(last_lines))
#    msg['Subject'] ='[API SERVER by Flask] PDF Upload complated'
#    msg['To'] = os.environ['EMAIL_HOST_USER_SEND']
#    smtp.sendmail(os.environ['EMAIL_HOST_USER'], os.environ['EMAIL_HOST_USER_SEND'].split(','), msg.as_string())
#    smtp.quit()

#    return last_lines


@application.route('/company_reg/cor_number/', methods=['POST'])
def parse_single():
    parse_start(request.form, 'cor_number')

    #if not application.debug:

    #    text = read_last_lines('flask.log',30)


    return 'success'


@application.route('/company_reg/versions/', methods=['POST'])
def parse():
    parse_start(request.form, 'previous_version')
    #if not application.debug:
    #    text = read_last_lines('flask.log',30)
    return 'success'

@application.route('/company_reg/cor_numbers/', methods=['POST'])
def parse_vesrions():
    parse_start(request.form, 'cor_numbers')
    #if not application.debug:
    #    text = read_last_lines('flask.log',30)
    return 'success'

@application.route('/company_reg/date/', methods=['POST'])
def parse_date():
    parse_start(request.form, 'date')
    #if not application.debug:
    #    text = read_last_lines('flask.log',30)
    return 'success'


if __name__ == '__main__':
    if not application.debug:
        application.run(host='0.0.0.0', port=80)
    else:
        application.run(host='127.0.0.1', port=8888)




