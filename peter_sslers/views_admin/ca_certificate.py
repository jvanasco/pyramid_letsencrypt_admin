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
from ..lib.forms import (Form_CACertificate_Upload__file,
                         Form_CACertificate_UploadBundle__file,
                         )
from ..lib import acme as lib_acme
from ..lib import cert_utils as lib_cert_utils
from ..lib import db as lib_db
from ..lib import letsencrypt_info as lib_letsencrypt_info
from ..lib.handler import Handler, items_per_page


# ==============================================================================


class ViewAdmin(Handler):

    @view_config(route_name='admin:ca_certificates', renderer='/admin/ca_certificates.mako')
    @view_config(route_name='admin:ca_certificates_paginated', renderer='/admin/ca_certificates.mako')
    def ca_certificates(self):
        items_count = lib_db.get__LetsencryptCACertificate__count(self.request.dbsession)
        (pager, offset) = self._paginate(items_count, url_template='/.well-known/admin/ca-certificates/{0}')
        items_paged = lib_db.get__LetsencryptCACertificate__paginated(self.request.dbsession, limit=items_per_page, offset=offset)
        return {'project': 'peter_sslers',
                'LetsencryptCACertificates_count': items_count,
                'LetsencryptCACertificates': items_paged,
                'pager': pager,
                }

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _ca_certificate_focus(self):
        dbLetsencryptCACertificate = lib_db.get__LetsencryptCACertificate__by_id(self.request.dbsession, self.request.matchdict['id'])
        if not dbLetsencryptCACertificate:
            raise HTTPNotFound('the cert was not found')
        return dbLetsencryptCACertificate

    @view_config(route_name='admin:ca_certificate:focus', renderer='/admin/ca_certificate-focus.mako')
    def ca_certificate_focus(self):
        dbLetsencryptCACertificate = self._ca_certificate_focus()
        items_count = lib_db.get__LetsencryptServerCertificate__by_LetsencryptCACertificateId__count(
            self.request.dbsession, dbLetsencryptCACertificate.id)
        items_paged = lib_db.get__LetsencryptServerCertificate__by_LetsencryptCACertificateId__paginated(
            self.request.dbsession, dbLetsencryptCACertificate.id, limit=10, offset=0)
        return {'project': 'peter_sslers',
                'LetsencryptCACertificate': dbLetsencryptCACertificate,
                'LetsencryptServerCertificates_count': items_count,
                'LetsencryptServerCertificates': items_paged,
                }

    @view_config(route_name='admin:ca_certificate:focus:raw', renderer='string')
    def ca_certificate_focus_raw(self):
        dbLetsencryptCACertificate = self._ca_certificate_focus()
        if self.request.matchdict['format'] == 'pem':
            self.request.response.content_type = 'application/x-pem-file'
            return dbLetsencryptCACertificate.cert_pem
        elif self.request.matchdict['format'] == 'pem.txt':
            return dbLetsencryptCACertificate.cert_pem
        elif self.request.matchdict['format'] in ('cer', 'crt', 'der'):
            as_der = lib_cert_utils.convert_pem_to_der(pem_data=dbLetsencryptCACertificate.cert_pem)
            response = Response()
            if self.request.matchdict['format'] in ('crt', 'der'):
                response.content_type = 'application/x-x509-ca-cert'
            elif self.request.matchdict['format'] in ('cer', ):
                response.content_type = 'application/pkix-cert'
            response.body = as_der
            return response
        return 'chain.?'

    @view_config(route_name='admin:ca_certificate:focus:parse.json', renderer='json')
    def ca_certificate_focus_parse_json(self):
        dbLetsencryptCACertificate = self._ca_certificate_focus()
        return {"%s" % dbLetsencryptCACertificate.id: lib_cert_utils.parse_cert(cert_pem=dbLetsencryptCACertificate.cert_pem),
                }

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(route_name='admin:ca_certificate:focus:signed_certificates', renderer='/admin/ca_certificate-focus-signed_certificates.mako')
    @view_config(route_name='admin:ca_certificate:focus:signed_certificates_paginated', renderer='/admin/ca_certificate-focus-signed_certificates.mako')
    def ca_certificate_focus__signed_certificates(self):
        dbLetsencryptCACertificate = self._ca_certificate_focus()
        items_count = lib_db.get__LetsencryptServerCertificate__by_LetsencryptCACertificateId__count(
            self.request.dbsession, dbLetsencryptCACertificate.id)
        (pager, offset) = self._paginate(items_count, url_template='/.well-known/admin/ca-certificate/%s/signed_certificates/{0}' % dbLetsencryptCACertificate.id)
        items_paged = lib_db.get__LetsencryptServerCertificate__by_LetsencryptCACertificateId__paginated(
            self.request.dbsession, dbLetsencryptCACertificate.id, limit=items_per_page, offset=offset)
        return {'project': 'peter_sslers',
                'LetsencryptCACertificate': dbLetsencryptCACertificate,
                'LetsencryptServerCertificates_count': items_count,
                'LetsencryptServerCertificates': items_paged,
                'pager': pager,
                }

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(route_name='admin:ca_certificate:upload')
    @view_config(route_name='admin:ca_certificate:upload.json', renderer='json')
    def ca_certificate_upload(self):
        if self.request.POST:
            return self._ca_certificate_upload__submit()
        return self._ca_certificate_upload__print()

    def _ca_certificate_upload__print(self):
        if self.request.matched_route.name == 'admin:ca_certificate:upload.json':
            return {'instructions': """curl --form 'chain_file=@chain1.pem' --form http://127.0.0.1:6543/.well-known/admin/ca-certificate/upload.json""",
                    'form_fields': {'chain_file': 'required',
                                    },
                    }
        return render_to_response("/admin/ca_certificate-new.mako", {}, self.request)

    def _ca_certificate_upload__submit(self):
        try:
            (result, formStash) = formhandling.form_validate(self.request,
                                                             schema=Form_CACertificate_Upload__file,
                                                             validate_get=False
                                                             )
            if not result:
                raise formhandling.FormInvalid()

            chain_pem = formStash.results['chain_file'].file.read()
            chain_file_name = formStash.results['chain_file_name'] or 'manual upload'
            dbLetsencryptCACertificate, cacert_is_created = lib_db.getcreate__LetsencryptCACertificate__by_pem_text(
                self.request.dbsession,
                chain_pem,
                chain_file_name
            )

            if self.request.matched_route.name == 'admin:ca_certificate:upload.json':
                return {'result': 'success',
                        'ca_certificate': {'created': cacert_is_created,
                                           'id': dbLetsencryptCACertificate.id,
                                           },
                        }
            return HTTPFound('/.well-known/admin/ca-certificate/%s?is_created=%s' % (dbLetsencryptCACertificate.id, (1 if cacert_is_created else 0)))

        except formhandling.FormInvalid, e:
            formStash.set_error(field="Error_Main",
                                message="There was an error with your form.",
                                raise_FormInvalid=False,
                                message_prepend=True
                                )
            if self.request.matched_route.name == 'admin:ca_certificate:upload.json':
                return {'result': 'error',
                        'form_errors': formStash.errors,
                        }
            return formhandling.form_reprint(
                self.request,
                self._ca_certificate_upload__print,
                auto_error_formatter=formhandling.formatter_none,
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(route_name='admin:ca_certificate:upload_bundle')
    @view_config(route_name='admin:ca_certificate:upload_bundle.json', renderer='json')
    def ca_certificate_upload_bundle(self):
        if self.request.POST:
            return self._ca_certificate_upload_bundle__submit()
        return self._ca_certificate_upload_bundle__print()

    def _ca_certificate_upload_bundle__print(self):
        if self.request.matched_route.name == 'admin:ca_certificate:upload_bundle.json':
            _instructions = ["curl --form 'isrgrootx1_file=@isrgrootx1.pem'", ]
            _form_fields = {'isrgrootx1_file': 'optional'}
            for xi in lib_letsencrypt_info.CA_CROSS_SIGNED_X:
                _instructions.append("""--form 'le_%s_cross_signed_file=@lets-encrypt-%s-cross-signed.pem'""" % (xi, xi))
                _form_fields['le_%s_cross_signed_file' % xi] = 'optional'
            for xi in lib_letsencrypt_info.CA_AUTH_X:
                _instructions.append("""--form 'le_%s_auth_file=@letsencryptauthority%s'""" % (xi, xi))
                _form_fields['le_%s_auth_file' % xi] = 'optional'
            # and the post
            _instructions.append("""http://127.0.0.1:6543/.well-known/admin/ca-certificate/upload-bundle.json""")

            return {'instructions': ' '.join(_instructions),
                    'form_fields': _form_fields
                    }
        return render_to_response("/admin/ca_certificate-new_bundle.mako",
                                  {'CA_CROSS_SIGNED_X': lib_letsencrypt_info.CA_CROSS_SIGNED_X,
                                   'CA_AUTH_X': lib_letsencrypt_info.CA_AUTH_X,
                                   },
                                  self.request)

    def _ca_certificate_upload_bundle__submit(self):
        try:
            (result, formStash) = formhandling.form_validate(self.request,
                                                             schema=Form_CACertificate_UploadBundle__file,
                                                             validate_get=False
                                                             )
            if not result:
                raise formhandling.FormInvalid()
            has_uploads = [i for i in formStash.results.values() if i is not None]
            if not has_uploads:
                formStash.set_error(field="Error_Main",
                                    message="Nothing uploaded!",
                                    raise_FormInvalid=True,
                                    )

            bundle_data = {'isrgrootx1_pem': None,
                           }
            if formStash.results['isrgrootx1_file'] is not None:
                bundle_data['isrgrootx1_pem'] = formStash.results['isrgrootx1_file'].file.read()

            for xi in lib_letsencrypt_info.CA_CROSS_SIGNED_X:
                bundle_data['le_%s_cross_signed_pem' % xi] = None
                if formStash.results['le_%s_cross_signed_file' % xi] is not None:
                    bundle_data['le_%s_cross_signed_pem' % xi] = formStash.results['le_%s_cross_signed_file' % xi].file.read()

            for xi in lib_letsencrypt_info.CA_AUTH_X:
                bundle_data['le_%s_auth_pem' % xi] = None
                if formStash.results['le_%s_auth_file' % xi] is not None:
                    bundle_data['le_%s_auth_pem' % xi] = formStash.results['le_%s_auth_file' % xi].file.read()

            bundle_data = dict([i for i in bundle_data.items() if i[1]])

            dbResults = lib_db.upload__LetsencryptCACertificateBundle__by_pem_text(
                self.request.dbsession,
                bundle_data
            )

            if self.request.matched_route.name == 'admin:ca_certificate:upload_bundle.json':
                rval = {'result': 'success'}
                for (cert_type, cert_result) in dbResults.items():
                    rval[cert_type] = {'created': cert_result[1],
                                       'id': cert_result[0].id,
                                       }
                return rval
            return HTTPFound('/.well-known/admin/ca-certificates?uploaded=1')

        except formhandling.FormInvalid, e:
            formStash.set_error(field="Error_Main",
                                message="There was an error with your form.",
                                raise_FormInvalid=False,
                                message_prepend=True
                                )
            if self.request.matched_route.name == 'admin:ca_certificate:upload_bundle.json':
                return {'result': 'error',
                        'form_errors': formStash.errors,
                        }
            return formhandling.form_reprint(
                self.request,
                self._ca_certificate_upload_bundle__print,
                auto_error_formatter=formhandling.formatter_none,
            )
