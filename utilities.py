import datetime

def parseTimeString(timeString):
	#Receive a string of the form hh:mm:ss, return a datetime timedelta object
	hms = str.split(timeString,':')
	if (len(hms) == 3 and int(hms[0]) and int(hms[1]) and int(hms[2])):
		tDelta = datetime.timedelta(hours = int(hms[0]), minutes = int(hms[1]), seconds = int(hms[2]))
	else:
		tDelta = datetime.timedelta()
	return tDelta