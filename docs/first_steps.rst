First Steps
============

Next to the basic steps to get a Django instance running there are some juntagrico specific steps which have to be taken.

Member for Superuser
--------------------
Your superuser requires a Member object which is generated using the django management command :command:`create_member_for_superusers`

Initial List Generation
-----------------------
The depot lists are created by the following django management command :command:`generate_depot_list`. This command can
be called manually or using a cronjob.

Configure the Website Name and Domain
-------------------------------------
The website name and domain are displayed in various places on the website and in some emails.
In the Django-Admin under Websites edit the `example.com` entry
and set the names to your website domain and display name.
