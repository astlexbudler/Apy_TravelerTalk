# apptoaster/hosts.py

from django_hosts import patterns, host

host_patterns = patterns(
    '',
    host(r'', 'apptoaster.urls', name='main'),
    host(r'partner', 'app_partner.urls', name='app_partner'),
    host(r'spv', 'app_supervisor.urls', name='app_supervisor'),
)
