import datetime

def parseTimeString(timeString):
	#Receive a string of the form hh:mm:ss, return a datetime timedelta object
	hms = str.split(timeString,':')
	if (len(hms) == 3):
		tDelta = datetime.timedelta(hours = int(hms[0]), minutes = int(hms[1]), seconds = int(hms[2]))
	else:
		tDelta = datetime.timedelta()
	return tDelta

#Remove all whitespace characters from everywhere in a string or unicode object
def stripString(stringy):
	return "".join(stringy.split())