from django_cron import cronScheduler, Job


class Test(Job):
    # how often to execute, in seconds
    run_every = 1

    def job(self):
        print "running"



#cronScheduler.register(Test)

