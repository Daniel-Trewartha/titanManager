from sqlalchemy import create_engine
from base import Base

def main():
    #xml input
    #Take job as argument??
    #should be executable or argument for executable?

    #Have queue(database reqd.?)
    #Check Titan queue
    #submit if necessary
    #nurse job to good health
    #check success: output file presence(non-0 size), pbs report

    engine = create_engine('sqlite:///:memory:',echo=True)
    import job
    testJob = job.Job(jobName='testjob')
    print testJob.jobName
    print("HI")

if __name__ == '__main__':
    main()
