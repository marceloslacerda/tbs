import datetime

schedule = '* * * * *'

message = 'test message'

print(message + ' ' + datetime.datetime.now().isoformat())
