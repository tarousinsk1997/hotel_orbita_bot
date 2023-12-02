from datetime import datetime, date, time, timedelta, timezone
import ssl

d = date(2023, 11, 20)
t = time(22, 0)

dt = datetime.combine(d, t)

dt_now =datetime.now()


dt_delta = dt_now - dt

if dt_delta > timedelta(0,0,0,0,20,0,0):
    print('True')


test = '2023-12-10T00:00:00'



print(ssl.get_default_verify_paths())



#print(datetime.strptime(test, '%Y-%m-%dT%H:%M:%S'))

