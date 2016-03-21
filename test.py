import json
from datetime import datetime
from time import sleep
def decode(data, default={}):
        print data
        try:
            print json.loads(data)
            return json.loads(data)
        except ValueError as e:
            print "eee", e, default
            return default

def log(message, when=datetime.now()):
    print('%s: %s' % (when, message))

def sort_priority2(numbers, group):
    found = False
    def helper(x):
        if x in group:
            found = True # Seems simple
            return (0, x)
        return (1, x)
    numbers.sort(key=helper)
    return found

def sort_priority(numbers, group):
    found = [False]
    def helper(x):
        if x in group:
            found[0] = True
            return (0, x)
        return (1, x)
    numbers.sort(key=helper)
    return found[0]

if __name__ == "__main__":
    log('Hi there!')
    sleep(0.1)
    log('Hi again!')
    foo = decode('bad data')
    foo['stuff'] = 5
    bar = decode('also bad')
    bar['meep'] = 1
    go = decode('also go')
    go['haha'] = 2
    print('Foo:', foo)
    print('Bar:', bar)
    print('Go:', go)
    numbers = [8, 3, 1, 2, 5, 4, 7, 6]
    group = {2, 3, 5, 7}
    found = sort_priority(numbers, group)
    print('Found:', found)
    print(numbers)