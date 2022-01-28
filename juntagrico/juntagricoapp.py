from juntagrico.util import addons

# register template hooks

addons.config.template.register('user_menu', ['menu/entries/' + n + '.html' for n in [
    'subscription',
    'jobs',
    'deliveries',
    'activityareas',
    'membership',
    'contact'
]])

addons.config.template.register('user_menu_jobs', ['menu/entries/jobs/' + n + '.html' for n in [
    'my',
    'all'
]])

addons.config.template.register('home', ['widgets/home/' + n + '.html' for n in [
    'jobs',
    'activityareas'
]])

addons.config.template.register('pre_job')
