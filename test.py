# -*- coding: utf-8 -*-
from threading import Thread
import time


def echo(args):
    s = input('ss')
    print('s')


def f(args):
    args.i += 1
    print('f')


class MyThread(Thread):
    def __init__(self, i):
        Thread.__init__(self)
        self.i = i

    def run(self):
        while 1:
            self.i += 1
            print(self.i)


class MyThread2(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.s = 0

    def run(self):
        while 1:
            self.s = input('shuru')


def add1(*x):
    x[0] = x + 1


if __name__ == '__main__':
    x = 1
    add1(x)
    print(x)
