#-*- coding: utf-8 -*-

# Copyright (c) 2011 Moxie Marlinspike
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#

from convergence.verifier import Verifier, OptionsError

import twisted.names.client
import logging

log = logging.getLogger(__name__)


class DNSVerifier(Verifier):
    '''
    This class is responsible for checking a certificate fingerprint
    via a DNS-based certificate catalog
    '''

    description = 'Check certificate fingerprint via a DNS-based certificate catalog.'
    options_description = 'Hostname of the DNS server to query (required).'

    def __init__(self, host):
        if host is None:
            raise OptionsError('DNS host to query must be specified as a backend option.')
        super(DNSVerifier, self).__init__()
        self.host = host

    def _dnsLookupComplete(self, result, fingerprint, log):
        log.debug('Catalog result: ' + str(result[0][0].payload.data[0]))
        return (200, fingerprint)

    def _dnsLookupError(self, error, log):
        log.debug('Catalog resolution failure: ' + str(error))
        return (409, None)

    def verify(self, host, port, address, fingerprint, log):
        formatted = ''.join(fingerprint.split(':')).lower()
        deferred = twisted.names.client.lookupText('%s.%s' % (formatted, self.host))

        deferred.addCallback(self._dnsLookupComplete, fingerprint, log)
        deferred.addErrback(self._dnsLookupError, log)

        return deferred


verifier = DNSVerifier
