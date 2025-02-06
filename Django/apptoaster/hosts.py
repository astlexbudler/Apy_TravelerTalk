# apptoaster/hosts.py

from django_hosts import patterns, host

host_patterns = patterns(
    '',
    host(r'', 'apptoaster.urls', name='main'),
    host(r'partner', 'apptoaster.urls', name='partner'),
    host(r'spv', 'apptoaster.urls', name='spv'),
)
