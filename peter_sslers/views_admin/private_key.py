# pyramid
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.renderers import render, render_to_response
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound

# stdlib
import datetime
import pdb

# pypi
import pyramid_formencode_classic as formhandling
import sqlalchemy

# localapp
from ..models import *
from ..lib.forms import (Form_PrivateKey_new__file,
                         Form_PrivateKey_Mark,
                         )
from ..lib import acme as lib_acme
from ..lib import db as lib_db
from ..lib import events as lib_events
from ..lib import cert_utils as lib_cert_utils
from ..lib.handler import Handler, items_per_page


# ==============================================================================


class ViewAdmin(Handler):

    @view_config(route_name='admin:private_keys', renderer='/admin/private_keys.mako')
    @view_config(route_name='admin:private_keys_paginated', renderer='/admin/private_keys.mako')
    def private_keys(self):
        items_count = lib_db.get__SslPrivateKey__count(self.request.dbsession)
        (pager, offset) = self._paginate(items_count, url_template='%s/private-keys/{0}' % self.request.registry.settings['admin_prefix'])
        items_paged = lib_db.get__SslPrivateKey__paginated(self.request.dbsession, limit=items_per_page, offset=offset)
        return {'project': 'peter_sslers',
                'SslPrivateKeys_count': items_count,
                'SslPrivateKeys': items_paged,
                'pager': pager,
                }

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _private_key_focus(self, eagerload_web=False):
        dbSslPrivateKey = lib_db.get__SslPrivateKey__by_id(self.request.dbsession, self.request.matchdict['id'], eagerload_web=eagerload_web, )
        if not dbSslPrivateKey:
            raise HTTPNotFound('the key was not found')
        return dbSslPrivateKey

    @view_config(route_name='admin:private_key:focus', renderer='/admin/private_key-focus.mako')
    def private_key_focus(self):
        dbSslPrivateKey = self._private_key_focus(eagerload_web=True)
        return {'project': 'peter_sslers',
                'SslPrivateKey': dbSslPrivateKey
                }

    @view_config(route_name='admin:private_key:focus:raw', renderer='string')
    def private_key_focus_raw(self):
        dbSslPrivateKey = self._private_key_focus()
        if self.request.matchdict['format'] == 'pem':
            self.request.response.content_type = 'application/x-pem-file'
            return dbSslPrivateKey.key_pem
        elif self.request.matchdict['format'] == 'pem.txt':
            return dbSslPrivateKey.key_pem
        elif self.request.matchdict['format'] == 'key':
            self.request.response.content_type = 'application/pkcs8'
            as_der = lib_cert_utils.convert_pem_to_der(pem_data=dbSslPrivateKey.key_pem)
            return as_der

    @view_config(route_name='admin:private_key:focus:parse.json', renderer='json')
    def private_key_focus_parse_json(self):
        dbSslPrivateKey = self._private_key_focus()
        return {"%s" % dbSslPrivateKey.id: lib_cert_utils.parse_key(key_pem=dbSslPrivateKey.key_pem),
                }

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(route_name='admin:private_key:focus:certificates', renderer='/admin/private_key-focus-certificates.mako')
    @view_config(route_name='admin:private_key:focus:certificates_paginated', renderer='/admin/private_key-focus-certificates.mako')
    def private_key_focus__certificates(self):
        dbSslPrivateKey = self._private_key_focus()
        items_count = lib_db.get__SslServerCertificate__by_SslPrivateKeyId__count(
            self.request.dbsession, dbSslPrivateKey.id)
        (pager, offset) = self._paginate(items_count, url_template='%s/private-key/%s/certificates/{0}' % (self.request.registry.settings['admin_prefix'], dbSslPrivateKey.id))
        items_paged = lib_db.get__SslServerCertificate__by_SslPrivateKeyId__paginated(
            self.request.dbsession, dbSslPrivateKey.id, limit=items_per_page, offset=offset)
        return {'project': 'peter_sslers',
                'SslPrivateKey': dbSslPrivateKey,
                'SslServerCertificates_count': items_count,
                'SslServerCertificates': items_paged,
                'pager': pager,
                }

    @view_config(route_name='admin:private_key:focus:certificate_requests', renderer='/admin/private_key-focus-certificate_requests.mako')
    @view_config(route_name='admin:private_key:focus:certificate_requests_paginated', renderer='/admin/private_key-focus-certificate_requests.mako')
    def private_key_focus__certificate_requests(self):
        dbSslPrivateKey = self._private_key_focus()
        items_count = lib_db.get__SslCertificateRequest__by_SslPrivateKeyId__count(
            self.request.dbsession, dbSslPrivateKey.id)
        (pager, offset) = self._paginate(items_count, url_template='%s/private-key/%s/certificate-requests/{0}' % (self.request.registry.settings['admin_prefix'], dbSslPrivateKey.id))
        items_paged = lib_db.get__SslCertificateRequest__by_SslPrivateKeyId__paginated(
            self.request.dbsession, dbSslPrivateKey.id, limit=items_per_page, offset=offset)
        return {'project': 'peter_sslers',
                'SslPrivateKey': dbSslPrivateKey,
                'SslCertificateRequests_count': items_count,
                'SslCertificateRequests': items_paged,
                'pager': pager,
                }

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(route_name='admin:private_key:new')
    def private_key_new(self):
        if self.request.POST:
            return self._private_key_new__submit()
        return self._private_key_new__print()

    def _private_key_new__print(self):
        return render_to_response("/admin/private_key-new.mako", {}, self.request)

    def _private_key_new__submit(self):
        try:
            (result, formStash) = formhandling.form_validate(self.request,
                                                             schema=Form_PrivateKey_new__file,
                                                             validate_get=False
                                                             )
            if not result:
                raise formhandling.FormInvalid()

            private_key_pem = formStash.results['private_key_file'].file.read()
            dbSslPrivateKey, _is_created = lib_db.getcreate__SslPrivateKey__by_pem_text(self.request.dbsession, private_key_pem)

            return HTTPFound('%s/private_key/%s%s' % (self.request.registry.settings['admin_prefix'], dbSslPrivateKey.id, ('?is_created=1' if _is_created else '')))

        except formhandling.FormInvalid, e:
            formStash.set_error(field="Error_Main",
                                message="There was an error with your form.",
                                raise_FormInvalid=False,
                                message_prepend=True
                                )
            return formhandling.form_reprint(
                self.request,
                self._private_key_new__print,
                auto_error_formatter=formhandling.formatter_none,
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(route_name='admin:private_key:focus:mark', renderer=None)
    @view_config(route_name='admin:private_key:focus:mark.json', renderer='json')
    def certificate_focus_mark(self):
        dbSslPrivateKey = self._private_key_focus()
        action = '!MISSING or !INVALID'
        try:
            (result, formStash) = formhandling.form_validate(self.request,
                                                             schema=Form_PrivateKey_Mark,
                                                             validate_get=True
                                                             )
            if not result:
                raise formhandling.FormInvalid()

            action = formStash.results['action']
            event_type = SslOperationsEventType.private_key_mark
            event_payload = {'private_key_id': dbSslPrivateKey.id,
                             'action': formStash.results['action'],
                             'v': 1,
                             }
            marked_comprimised = False
            if action == 'deactivate':
                if not dbSslPrivateKey.is_active:
                    raise formhandling.FormInvalid('Already deactivated')
                dbSslPrivateKey.is_active = False
            elif action == 'activate':
                if dbSslPrivateKey.is_active:
                    raise formhandling.FormInvalid('Already activated')
                if dbSslPrivateKey.is_compromised:
                    raise formhandling.FormInvalid('Can not activate a compromised key')
                dbSslPrivateKey.is_active = True
            elif action == 'compromised':
                if dbSslPrivateKey.is_compromised:
                    raise formhandling.FormInvalid('Already compromised')
                dbSslPrivateKey.is_active = False
                dbSslPrivateKey.is_compromised = True
                event_type = SslOperationsEventType.private_key_revoke
                marked_comprimised = True
            else:
                raise formhandling.FormInvalid('invalid `action`')

            self.request.dbsession.flush()

            # bookkeeping
            operationsEvent = lib_db.create__SslOperationsEvent(
                self.request.dbsession,
                event_type,
                event_payload,
            )
            if marked_comprimised:
                lib_events.PrivateKey_compromised(
                    self.request.dbsession,
                    dbSslPrivateKey,
                    operationsEvent
                )
            url_success = '%s/private-key/%s?operation=mark&action=%s&result=sucess' % (
                self.request.registry.settings['admin_prefix'],
                dbSslPrivateKey.id,
                action,
            )
            return HTTPFound(url_success)

        except formhandling.FormInvalid, e:
            formStash.set_error(field="Error_Main",
                                message="There was an error with your form.",
                                raise_FormInvalid=False,
                                message_prepend=True
                                )
            url_failure = '%s/private-key/%s?operation=mark&action=%s&result=error&error=%s' % (
                self.request.registry.settings['admin_prefix'],
                dbSslPrivateKey.id,
                action,
                e.message,
            )
            raise HTTPFound(url_failure)
