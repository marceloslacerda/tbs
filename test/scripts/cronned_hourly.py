import datetime

schedule = '0 * * * *'

message = 'test hourly'

print(message + ' ' + datetime.datetime.now().isoformat())
