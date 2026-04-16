import gettext

translation = gettext.translation('localecounter2', 'po', fallback=True)
_, ngettext = translation.gettext, translation.ngettext
translation2 = gettext.translation('localecounter2', 'po', fallback=True)
_2, ngettext2 = translation.gettext, translation.ngettext


while s := input():
	n = len(s.split())
	print(ngettext2("Written {} word", "Written {} words", n).format(n))
	print(ngettext("Entered {} word", "Entered {} words", n).format(n))
	
