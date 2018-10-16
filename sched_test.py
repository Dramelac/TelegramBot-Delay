import sched, time

s = sched.scheduler(time.time, time.sleep)


def print_time(a='default'):
    print("From print_time", time.time(), a)


print("start", time.time())
s.enter(10, 1, print_time)
s.enter(5, 2, print_time, argument=('positional',))
s.enter(5, 1, print_time, kwargs={'a': 'keyword'})
print("mid", time.time())
s.run()
print("end", time.time())
