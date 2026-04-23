def func(a, b, c):
	if a == 0:
		raise ValueError()
	elif b**2 - 4 * a * c > 0:
		return (2)
	elif b**2 - 4 * a * c == 0:
		return (1)
	else:
		return (0)
