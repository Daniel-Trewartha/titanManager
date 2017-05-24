from base import Base,Session,engine
import time
import os
import job


def main():
    #xml input
    #Take job as argument??
    #should be executable or argument for executable?

    #Have queue(database reqd.?)
    #Check Titan queue
    #submit if necessary
    #nurse job to good health
    #check success: output file presence(non-0 size), pbs report
    Base.metadata.create_all(engine)

    outputDir = os.path.split(os.path.abspath(__file__))[0]
    outputFiles = "output.txt"
    testJob = job.Job(jobName="TestJob",outputDir=outputDir,outputFiles=outputFiles,executionCommand="echo 'test' >> "+os.path.join(outputDir,outputFiles))
    Session.add(testJob)
    print testJob.jobName
    print testJob.pbsID
    print testJob.checkStatus()
    testJob.submit()
    time.sleep(10)
    print testJob.checkStatus()
    time.sleep(60)
    print testJob.checkStatus()
    print testJob.pbsID
    Session.commit()

if __name__ == '__main__':
    main()
