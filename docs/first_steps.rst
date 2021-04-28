First steps
============

Next to the basic steps to get a Django instance running there are some juntagrico specific steps which have to be taken.

Member for superuser
--------------------
Your superuser requires a Member object  which is generated using the django management command :command:`create_member_for_superusers`

Initial List generation
-----------------------
The depot lists are created by the following django management command :command:`generate_depot_list`. This command can
be called manually or using a cronjob.

