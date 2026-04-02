from math import *


def genarray():
    'This is docstring for my function'


l = [
    [f"this is {sin(x)}" for x in range(5)] for i in range(7)
]
print(
    '\n'.join('|'.join(l[i]) for i in range(len(l))))
