= How to install djang-cron =

1. Put 'django_cron' into your python path

2. Add 'django_cron' to INSTALLED_APPS in your settings.py file

3. Add the following code to the beginning of your urls.py file (just after the imports): 

	import django_cron
	django_cron.autodiscover()


4. Create a file called 'cron.py' inside each installed app that you want to add a recurring job to. The app must be installed via the INSTALLED_APPS in your settings.py or the autodiscover will not find it.

=== Important note ===

If you are using mod_python, you need to make sure your server is set up to server more than one request per instance, Otherwise it will kill django-cron before the tasks get started. The specific line to look for is in your 'httpd.conf' file:


	# THIS IS BAD!!! IT WILL CRIPPLE DJANGO-CRON
	MaxRequestsPerChild 1

	
Change it to a value that is large enough that your cron jobs will get run at least once per instance. We're working on resolving this issue without dictating your server config. 

In the meantime, django_cron is best used to execute tasks that occur relatively often (at least once an hour). Try setting MaxRequestsPerChild to 50, 100, or 200

	# Depending on traffic, and your server config, a number between 50 and 500 is probably good
	# Note: the higher this number, the more memory django is likely to use. Be careful on shared hosting
	MaxRequestsPerChild 100


== Example cron.py ==

from django_cron import cronScheduler, Job

# This is a function I wrote to check a feedback email address
# and add it to our database. Replace with your own imports
from MyMailFunctions import check_feedback_mailbox

class CheckMail(Job):
	"""
	Cron Job that checks the lgr users mailbox and adds any 
	approved senders' attachments to the db
	"""

	# run every 300 seconds (5 minutes)
	run_every = 300
		
	def job(self):
		# This will be executed every 5 minutes
		check_feedback_mailbox()

cronScheduler.register(CheckMail)
