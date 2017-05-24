
#Job object:
    #Columns:
    #setup commands?
    #executable
    #aprun options
    #resources (nodes and time)
    #received date
    #status
    #run date (list?)
    #input
    #output
    #pbs id (list?)

    #methods:
    #create
    #getters/setters
    #check status
    #submit
    #cancel
    #check input/output files

from sqlalchemy import Column, Integer, String, Interval, DateTime, JSON
import datetime

class Job:
    def __init(self):
        __tablename__ = 'jobs'
        
        id = column(integer, primary_key=True)
        executionCommand = column(string)
        nodes = column(integer)
        wallTime = column(interval)
        receivedTime = column(datetime)
        status = column(string)
        inputFiles = column(json)
        outputFiles = column(json)
        pbsID = column(json)

def main():
    print("HI")

    

    
