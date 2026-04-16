import calendar
import sys 

def restcalend(inr: year, int: month)
    rawcalend = calendar.month(int(sys.argv[1]), int(sys.argv[2])).split('\n')
    lines_ptn = ' '.join('==' for i in range(7))
    rawcalend[0] = f'.. table:: {rawcalend[0].strip()}'
    rawcalend.insert(-1, lines_ptn)
    rawcalend.insert(2, lines_ptn)
    rawcalend.insert(1, lines_ptn)
    rawcalend.insert(-1, lines_ptn)
    rawcalend.insert(-1, '')

print('\n    '.join(rawcalend))

if __name__ == "__main__":
	with open("..doc/calend.rst", 'w+') as f:
		print(restmonth(2026, 4), file=f)
