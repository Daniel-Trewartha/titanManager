import datetime

def parseTimeString(timeString):
	#Receive a string of the form hh:mm:ss, return a datetime timedelta object
	hms = str.split(timeString,':')
	if (len(hms) == 3):
                #Check for slurm d-h:m:s format
                if '-' in hms[0]:
                        tDelta = datetime.timedelta(days = int(str.split(hms[0],'-')[0]), hours = int(str.split(hms[0],'-')[1]), minutes = int(hms[1]), seconds = int(hms[2]))
                else:
                        tDelta = datetime.timedelta(hours = int(hms[0]), minutes = int(hms[1]), seconds = int(hms[2]))
	else:
		tDelta = datetime.timedelta()
	return tDelta

#Remove all whitespace from everywhere in a string or unicode object
def stripWhiteSpace(stringy):
	noWhiteSpace = "".join(stringy.split())
	return noWhiteSpace

def stripSlash(stringy):
	noSlash = stringy.replace("/","").replace("\\","")
	return noSlash
