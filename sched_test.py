import _thread
import sched
import time

s = sched.scheduler(time.time, time.sleep)


def print_time(a='default'):
    print("From print_time", time.time(), a)


def add_task(msg, time):
    s.enter(time, 1, print_time, kwargs={'a': msg})
    s.run()


def main():
    print("start", time.time())
    # s.enter(5, 2, print_time, argument=('positional',))
    # s.enter(5, 1, print_time, kwargs={'a': 'keyword'})
    _thread.start_new_thread(add_task, ('pos1', 5))
    _thread.start_new_thread(add_task, ('pos2', 5))
    _thread.start_new_thread(add_task, ('pos3', 8))
    print("end", time.time())
    time.sleep(10)


main()
