# stdlib
import datetime
import json
import logging
import pdb
import tempfile

# pypi
import sqlalchemy
import transaction
from zope.sqlalchemy import mark_changed

# localapp
from ...models import *
from .. import acme
from .. import cert_utils
from .. import letsencrypt_info
from .. import errors
from .. import events
from .. import utils

# setup logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)

from .get import *


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def getcreate__LetsencryptAccountKey__by_pem_text(dbSession, key_pem):
    key_pem = cert_utils.cleanup_pem_text(key_pem)
    key_pem_md5 = utils.md5_text(key_pem)
    is_created = False
    dbKey = dbSession.query(LetsencryptAccountKey)\
        .filter(LetsencryptAccountKey.key_pem_md5 == key_pem_md5,
                LetsencryptAccountKey.key_pem == key_pem,
                )\
        .first()
    if not dbKey:
        try:
            _tmpfile = tempfile.NamedTemporaryFile()
            _tmpfile.write(key_pem)
            _tmpfile.seek(0)

            # validate
            cert_utils.validate_key__pem_filepath(_tmpfile.name)

            # grab the modulus
            key_pem_modulus_md5 = cert_utils.modulus_md5_key__pem_filepath(_tmpfile.name)
        except:
            raise
        finally:
            _tmpfile.close()
        dbKey = LetsencryptAccountKey()
        dbKey.timestamp_first_seen = datetime.datetime.utcnow()
        dbKey.key_pem = key_pem
        dbKey.key_pem_md5 = key_pem_md5
        dbKey.key_pem_modulus_md5 = key_pem_modulus_md5
        dbSession.add(dbKey)
        dbSession.flush()
        is_created = True
    return dbKey, is_created


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def getcreate__LetsencryptCACertificate__by_pem_text(
    dbSession,
    cert_pem,
    chain_name,
    le_authority_name = None,
    is_authority_certificate = None,
    is_cross_signed_authority_certificate = None,
):
    dbCertificate = get__LetsencryptCACertificate__by_pem_text(dbSession, cert_pem)
    is_created = False
    if not dbCertificate:
        cert_pem = cert_utils.cleanup_pem_text(cert_pem)
        cert_pem_md5 = utils.md5_text(cert_pem)
        try:
            _tmpfile = tempfile.NamedTemporaryFile()
            _tmpfile.write(cert_pem)
            _tmpfile.seek(0)

            # validate
            cert_utils.validate_cert__pem_filepath(_tmpfile.name)

            # grab the modulus
            cert_pem_modulus_md5 = cert_utils.modulus_md5_cert__pem_filepath(_tmpfile.name)

            dbCertificate = LetsencryptCACertificate()
            dbCertificate.name = chain_name or 'unknown'

            dbCertificate.le_authority_name = le_authority_name
            dbCertificate.is_ca_certificate = True
            dbCertificate.is_authority_certificate = is_authority_certificate
            dbCertificate.is_cross_signed_authority_certificate = is_cross_signed_authority_certificate
            dbCertificate.id_cross_signed_of = None
            dbCertificate.timestamp_first_seen = datetime.datetime.utcnow()
            dbCertificate.cert_pem = cert_pem
            dbCertificate.cert_pem_md5 = cert_pem_md5
            dbCertificate.cert_pem_modulus_md5 = cert_pem_modulus_md5

            dbCertificate.timestamp_signed = cert_utils.parse_startdate_cert__pem_filepath(_tmpfile.name)
            dbCertificate.timestamp_expires = cert_utils.parse_enddate_cert__pem_filepath(_tmpfile.name)
            dbCertificate.cert_subject = cert_utils.cert_single_op__pem_filepath(_tmpfile.name, '-subject')
            dbCertificate.cert_subject_hash = cert_utils.cert_single_op__pem_filepath(_tmpfile.name, '-subject_hash')
            dbCertificate.cert_issuer = cert_utils.cert_single_op__pem_filepath(_tmpfile.name, '-issuer')
            dbCertificate.cert_issuer_hash = cert_utils.cert_single_op__pem_filepath(_tmpfile.name, '-issuer_hash')

            dbSession.add(dbCertificate)
            dbSession.flush()
            is_created = True
        except:
            raise
        finally:
            _tmpfile.close()

    return dbCertificate, is_created


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def getcreate__LetsencryptDomain__by_domainName(
    dbSession,
    domain_name,
    is_from_domain_queue=None,
):
    is_created = False
    dbDomain = get__LetsencryptDomain__by_name(dbSession, domain_name, preload=False)
    if not dbDomain:
        dbDomain = LetsencryptDomain()
        dbDomain.domain_name = domain_name
        dbDomain.timestamp_first_seen = datetime.datetime.utcnow()
        dbDomain.is_from_domain_queue = is_from_domain_queue
        dbSession.add(dbDomain)
        dbSession.flush()
        is_created = True
    return dbDomain, is_created


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def getcreate__LetsencryptPrivateKey__by_pem_text(dbSession, key_pem):
    key_pem = cert_utils.cleanup_pem_text(key_pem)
    key_pem_md5 = utils.md5_text(key_pem)
    is_created = False
    dbKey = dbSession.query(LetsencryptPrivateKey)\
        .filter(LetsencryptPrivateKey.key_pem_md5 == key_pem_md5,
                LetsencryptPrivateKey.key_pem == key_pem,
                )\
        .first()
    if not dbKey:
        try:
            _tmpfile = tempfile.NamedTemporaryFile()
            _tmpfile.write(key_pem)
            _tmpfile.seek(0)

            # validate
            cert_utils.validate_key__pem_filepath(_tmpfile.name)

            # grab the modulus
            key_pem_modulus_md5 = cert_utils.modulus_md5_key__pem_filepath(_tmpfile.name)
        except:
            raise
        finally:
            _tmpfile.close()

        dbKey = LetsencryptPrivateKey()
        dbKey.timestamp_first_seen = datetime.datetime.utcnow()
        dbKey.key_pem = key_pem
        dbKey.key_pem_md5 = key_pem_md5
        dbKey.key_pem_modulus_md5 = key_pem_modulus_md5
        dbSession.add(dbKey)
        dbSession.flush()
        is_created = True
    return dbKey, is_created


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def getcreate__LetsencryptServerCertificate__by_pem_text(
    dbSession,
    cert_pem,
    dbCACertificate=None,
    dbAccountKey=None,
    dbPrivateKey=None,
    letsencrypt_server_certificate_id__renewal_of=None,
):
    cert_pem = cert_utils.cleanup_pem_text(cert_pem)
    cert_pem_md5 = utils.md5_text(cert_pem)
    is_created = False
    dbCertificate = dbSession.query(LetsencryptServerCertificate)\
        .filter(LetsencryptServerCertificate.cert_pem_md5 == cert_pem_md5,
                LetsencryptServerCertificate.cert_pem == cert_pem,
                )\
        .first()
    if dbCertificate:
        if dbPrivateKey and (dbCertificate.letsencrypt_private_key_id__signed_by != dbPrivateKey.id):
            if dbCertificate.letsencrypt_private_key_id__signed_by:
                raise ValueError("Integrity Error. Competing PrivateKey (!?)")
            elif dbCertificate.letsencrypt_private_key_id__signed_by is None:
                dbCertificate.letsencrypt_private_key_id__signed_by = dbPrivateKey.id
                dbPrivateKey.count_certificates_issued += 1
                if not dbPrivateKey.timestamp_last_certificate_issue or (dbPrivateKey.timestamp_last_certificate_issue < dbCertificate.timestamp_signed):
                    dbPrivateKey.timestamp_last_certificate_issue = dbCertificate.timestamp_signed
                dbSession.flush()
        if dbAccountKey and (dbCertificate.letsencrypt_account_key_id != dbAccountKey.id):
            if dbCertificate.letsencrypt_account_key_id:
                raise ValueError("Integrity Error. Competing AccountKey (!?)")
            elif dbCertificate.letsencrypt_account_key_id is None:
                dbCertificate.letsencrypt_account_key_id = dbAccountKey.id
                dbAccountKey.count_certificates_issued += 1
                if not dbAccountKey.timestamp_last_certificate_issue or (dbAccountKey.timestamp_last_certificate_issue < dbCertificate.timestamp_signed):
                    dbAccountKey.timestamp_last_certificate_issue = dbAccountKey.timestamp_signed
                dbSession.flush()
    elif not dbCertificate:
        _tmpfileCert = None
        try:
            _tmpfileCert = tempfile.NamedTemporaryFile()
            _tmpfileCert.write(cert_pem)
            _tmpfileCert.seek(0)

            # validate
            cert_utils.validate_cert__pem_filepath(_tmpfileCert.name)

            dbCertificate = LetsencryptServerCertificate()
            _certificate_parse_to_record(_tmpfileCert, dbCertificate)

            dbCertificate.is_active = True
            dbCertificate.cert_pem = cert_pem
            dbCertificate.cert_pem_md5 = cert_pem_md5

            dbCertificate.letsencrypt_server_certificate_id__renewal_of = letsencrypt_server_certificate_id__renewal_of

            # this is the LetsEncrypt key
            if dbCACertificate is None:
                raise ValueError('dbCACertificate is None')
            # we should make sure it issued the certificate:
            if dbCertificate.cert_issuer_hash != dbCACertificate.cert_subject_hash:
                raise ValueError('dbCACertificate did not sign the certificate')
            dbCertificate.letsencrypt_ca_certificate_id__upchain = dbCACertificate.id

            # this is the private key
            # we should make sure it signed the certificate
            # the md5 check isn't exact, BUT ITS CLOSE
            if dbPrivateKey is None:
                raise ValueError('dbPrivateKey is None')
            if dbCertificate.cert_pem_modulus_md5 != dbPrivateKey.key_pem_modulus_md5:
                raise ValueError('dbPrivateKey did not sign the certificate')
            dbCertificate.letsencrypt_private_key_id__signed_by = dbPrivateKey.id
            dbPrivateKey.count_certificates_issued += 1
            if not dbPrivateKey.timestamp_last_certificate_issue or (dbPrivateKey.timestamp_last_certificate_issue < dbCertificate.timestamp_signed):
                dbPrivateKey.timestamp_last_certificate_issue = dbCertificate.timestamp_signed

            # did we submit an account key?
            if dbAccountKey:
                dbCertificate.letsencrypt_account_key_id = dbAccountKey.id
                dbAccountKey.count_certificates_issued += 1
                if not dbAccountKey.timestamp_last_certificate_issue or (dbAccountKey.timestamp_last_certificate_issue < dbAccountKey.timestamp_signed):
                    dbAccountKey.timestamp_last_certificate_issue = dbCertificate.timestamp_signed

            _subject_domain, _san_domains = cert_utils.parse_cert_domains__segmented(cert_path=_tmpfileCert.name)
            certificate_domain_names = _san_domains
            if _subject_domain is not None and _subject_domain not in certificate_domain_names:
                certificate_domain_names.insert(0, _subject_domain)
            if not certificate_domain_names:
                raise ValueError("could not find any domain names in the certificate")
            # getcreate__LetsencryptDomain__by_domainName returns a tuple of (domainObject, is_created)
            dbDomainObjects = [getcreate__LetsencryptDomain__by_domainName(dbSession, _domain_name)[0]
                               for _domain_name in certificate_domain_names]
            dbFqdnSet, is_created_fqdn = getcreate__LetsencryptUniqueFQDNSet__by_domainObjects(dbSession, dbDomainObjects)
            dbCertificate.letsencrypt_unique_fqdn_set_id = dbFqdnSet.id

            if len(certificate_domain_names) == 1:
                dbCertificate.is_single_domain_cert = True
            elif len(certificate_domain_names) > 1:
                dbCertificate.is_single_domain_cert = False

            dbSession.add(dbCertificate)
            dbSession.flush()
            is_created = True

        except:
            raise
        finally:
            if _tmpfileCert:
                _tmpfileCert.close()

    return dbCertificate, is_created


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def getcreate__LetsencryptUniqueFQDNSet__by_domainObjects(
    dbSession,
    domainObjects,
):
    is_created = False

    for dbDomain in domainObjects:
        if dbDomain not in dbSession:
            dbDomain = dbSession.merge(dbDomain)

    domain_ids = [dbDomain.id for dbDomain in domainObjects]
    domain_ids.sort()
    domain_ids_string = ','.join([str(id) for id in domain_ids])

    dbFQDNSet = dbSession.query(LetsencryptUniqueFQDNSet)\
        .filter(LetsencryptUniqueFQDNSet.domain_ids_string == domain_ids_string,
                )\
        .first()

    if not dbFQDNSet:
        dbFQDNSet = LetsencryptUniqueFQDNSet()
        dbFQDNSet.domain_ids_string = domain_ids_string
        dbFQDNSet.timestamp_first_seen = datetime.datetime.utcnow()
        dbSession.add(dbFQDNSet)
        dbSession.flush()

        for dbDomain in domainObjects:
            dbAssoc = LetsencryptUniqueFQDNSet2LetsencryptDomain()
            dbAssoc.letsencrypt_unique_fqdn_set_id = dbFQDNSet.id
            dbAssoc.letsencrypt_domain_id = dbDomain.id
            dbSession.add(dbAssoc)
            dbSession.flush()
        is_created = True

    return dbFQDNSet, is_created


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def create__CertificateRequest__by_domainNamesList_FLOW(dbSession, domain_names):
    # getcreate__LetsencryptDomain__by_domainName returns a tuple of (domainObject, is_created)
    dbDomainObjects = [getcreate__LetsencryptDomain__by_domainName(dbSession, _domain_name)[0]
                       for _domain_name in domain_names]
    dbFqdnSet, is_created_fqdn = getcreate__LetsencryptUniqueFQDNSet__by_domainObjects(dbSession, dbDomainObjects)

    dbLetsencryptCertificateRequest = LetsencryptCertificateRequest()
    dbLetsencryptCertificateRequest.is_active = True
    dbLetsencryptCertificateRequest.certificate_request_type_id = LetsencryptCertificateRequestType.FLOW
    dbLetsencryptCertificateRequest.timestamp_started = datetime.datetime.utcnow()
    dbLetsencryptCertificateRequest.letsencrypt_unique_fqdn_set_id = dbFqdnSet.id
    dbSession.add(dbLetsencryptCertificateRequest)
    dbSession.flush()

    for dbDomain in dbDomainObjects:
        dbLetsencryptCertificateRequest2D = LetsencryptCertificateRequest2LetsencryptDomain()
        dbLetsencryptCertificateRequest2D.letsencrypt_certificate_request_id = dbLetsencryptCertificateRequest.id
        dbLetsencryptCertificateRequest2D.letsencrypt_domain_id = dbDomain.id

        dbSession.add(dbLetsencryptCertificateRequest2D)
        dbSession.flush()

    dbSession.flush()

    return dbLetsencryptCertificateRequest


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def create__CertificateRequest__FULL(
    dbSession,
    domain_names,

    dbAccountKey=None,
    account_key_pem=None,

    dbPrivateKey=None,
    private_key_pem=None,

    letsencrypt_server_certificate_id__renewal_of=None,
):
    """

    #for a single domain
    openssl req -new -sha256 -key domain.key -subj "/CN=yoursite.com" > domain.csr

    #for multiple domains (use this one if you want both www.yoursite.com and yoursite.com)
    openssl req -new -sha256 -key domain.key -subj "/" -reqexts SAN -config <(cat /etc/ssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=DNS:yoursite.com,DNS:www.yoursite.com")) > domain.csr


    # homebrew?
    /usr/local/opt/openssl/bin/openssl req -new -sha256 -key domain.key -subj "/" -reqexts SAN -config <(cat /usr/local/etc/openssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=DNS:example.com,DNS:www.example.com")) > domain_multi.csr</code>


# scratch
openssl req -new -sha256 -key /var/folders/4o/4oYQL09OGcSwJ2-Uj2T+dE+++TI/-Tmp-/tmp9mT8V6 -subj "/" -reqexts SAN -config < /var/folders/4o/4oYQL09OGcSwJ2-Uj2T+dE+++TI/-Tmp-/tmpK9tsl9 >STDOUT
(cat /System/Library/OpenSSL/openssl.cnf <(printf "[SAN]\nsubjectAltName=DNS:yoursite.com,DNS:www.yoursite.com"))
cat /etc/ssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=DNS:yoursite.com,DNS:www.yoursite.com")
cat  /usr/local/etc/openssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=DNS:yoursite.com,DNS:www.yoursite.com")
cat /System/Library/OpenSSL/openssl.cnf printf "[SAN]\nsubjectAltName=DNS:yoursite.com,DNS:www.yoursite.com"
/usr/local/opt/openssl/bin/openssl req -new -sha256 -key domain.key -subj "/" -reqexts SAN -config <

    """
    if not any((dbAccountKey, account_key_pem)) or all((dbAccountKey, account_key_pem)):
        raise ValueError("Submit one and only one of: `dbAccountKey`, `account_key_pem`")

    if not any((dbPrivateKey, private_key_pem)) or all((dbPrivateKey, private_key_pem)):
        raise ValueError("Submit one and only one of: `dbPrivateKey`, `private_key_pem`")

    tmpfiles = []
    dbLetsencryptCertificateRequest = None
    dbLetsencryptServerCertificate = None
    try:

        # we should have cleaned this up before, but just be safe
        domain_names = [i.lower() for i in [d.strip() for d in domain_names] if i]
        domain_names = set(domain_names)
        if not domain_names:
            raise ValueError("no domain names!")
        # we need a list
        domain_names = list(domain_names)

        if dbAccountKey is None:
            account_key_pem = cert_utils.cleanup_pem_text(account_key_pem)
            dbAccountKey, _is_created = getcreate__LetsencryptAccountKey__by_pem_text(dbSession, account_key_pem)
        else:
            account_key_pem = dbAccountKey.key_pem
        # we need to use tmpfiles on the disk
        tmpfile_account = tempfile.NamedTemporaryFile()
        tmpfile_account.write(account_key_pem)
        tmpfile_account.seek(0)
        tmpfiles.append(tmpfile_account)

        if dbPrivateKey is None:
            private_key_pem = cert_utils.cleanup_pem_text(private_key_pem)
            dbPrivateKey, _is_created = getcreate__LetsencryptPrivateKey__by_pem_text(dbSession, private_key_pem)
        else:
            private_key_pem = dbPrivateKey.key_pem
        # we need to use tmpfiles on the disk
        tmpfile_pkey = tempfile.NamedTemporaryFile()
        tmpfile_pkey.write(private_key_pem)
        tmpfile_pkey.seek(0)
        tmpfiles.append(tmpfile_pkey)

        # make the CSR
        csr_text = acme.new_csr_for_domain_names(domain_names, tmpfile_pkey.name, tmpfiles)

        # store the csr_text in a tmpfile
        tmpfile_csr = tempfile.NamedTemporaryFile()
        tmpfile_csr.write(csr_text)
        tmpfile_csr.seek(0)
        tmpfiles.append(tmpfile_csr)

        # validate
        cert_utils.validate_csr__pem_filepath(tmpfile_csr.name)

        # grab the modulus
        csr_pem_modulus_md5 = cert_utils.modulus_md5_csr__pem_filepath(tmpfile_csr.name)

        # these MUST commit
        with transaction.manager as tx:

            # we'll use this tuple in a bit...
            # getcreate__LetsencryptDomain__by_domainName returns a tuple of (domainObject, is_created)
            dbDomainObjects = {_domain_name: getcreate__LetsencryptDomain__by_domainName(dbSession, _domain_name)[0] for _domain_name in domain_names}
            dbFqdnSet, is_created_fqdn = getcreate__LetsencryptUniqueFQDNSet__by_domainObjects(dbSession, dbDomainObjects.values())

            # build the cert
            dbLetsencryptCertificateRequest = LetsencryptCertificateRequest()
            dbLetsencryptCertificateRequest.is_active = True
            dbLetsencryptCertificateRequest.certificate_request_type_id = LetsencryptCertificateRequestType.FULL
            dbLetsencryptCertificateRequest.timestamp_started = datetime.datetime.utcnow()
            dbLetsencryptCertificateRequest.csr_pem = csr_text
            dbLetsencryptCertificateRequest.csr_pem_md5 = utils.md5_text(csr_text)
            dbLetsencryptCertificateRequest.csr_pem_modulus_md5 = csr_pem_modulus_md5
            dbLetsencryptCertificateRequest.letsencrypt_unique_fqdn_set_id = dbFqdnSet.id

            # note account/private keys
            dbLetsencryptCertificateRequest.letsencrypt_account_key_id = dbAccountKey.id
            dbLetsencryptCertificateRequest.letsencrypt_private_key_id__signed_by = dbPrivateKey.id
            dbLetsencryptCertificateRequest.letsencrypt_server_certificate_id__renewal_of = letsencrypt_server_certificate_id__renewal_of

            dbSession.add(dbLetsencryptCertificateRequest)
            dbSession.flush()

            # increment account/private key counts
            dbAccountKey.count_certificate_requests += 1
            dbPrivateKey.count_certificate_requests += 1
            t_now = datetime.datetime.utcnow()
            if not dbAccountKey.timestamp_last_certificate_request or (dbAccountKey.timestamp_last_certificate_request < t_now):
                dbAccountKey.timestamp_last_certificate_request = t_now
            if not dbPrivateKey.timestamp_last_certificate_request or (dbPrivateKey.timestamp_last_certificate_request < t_now):
                dbPrivateKey.timestamp_last_certificate_request = t_now

            dbSession.flush()

            # we'll use this tuple in a bit...
            for _domain_name in dbDomainObjects.keys():
                dbDomain = dbDomainObjects[_domain_name]

                dbLetsencryptCertificateRequest2D = LetsencryptCertificateRequest2LetsencryptDomain()
                dbLetsencryptCertificateRequest2D.letsencrypt_certificate_request_id = dbLetsencryptCertificateRequest.id
                dbLetsencryptCertificateRequest2D.letsencrypt_domain_id = dbDomain.id

                dbSession.add(dbLetsencryptCertificateRequest2D)
                dbSession.flush()

                # update the hash to be a tuple
                dbDomainObjects[_domain_name] = (dbDomain, dbLetsencryptCertificateRequest2D)

            dbSession.flush()

        def process_keyauth_challenge(domain, token, keyauthorization):
            log.info("-process_keyauth_challenge %s", domain)
            with transaction.manager as tx:
                (dbDomain, dbLetsencryptCertificateRequest2D) = dbDomainObjects[domain]
                dbDomain = dbSession.merge(dbDomain, )
                dbLetsencryptCertificateRequest2D = dbSession.merge(dbLetsencryptCertificateRequest2D, )
                dbLetsencryptCertificateRequest2D.challenge_key = token
                dbLetsencryptCertificateRequest2D.challenge_text = keyauthorization
                dbSession.flush()

        def process_keyauth_cleanup(domain, token, keyauthorization):
            log.info("-process_keyauth_cleanup %s", domain)

        # ######################################################################
        # THIS BLOCK IS FROM acme-tiny

        # parse account key to get public key
        header, thumbprint = acme.account_key__header_thumbprint(account_key_path=tmpfile_account.name, )

        # pull domains from csr
        csr_domains = cert_utils.parse_csr_domains(csr_path=tmpfile_csr.name,
                                                   submitted_domain_names=domain_names,
                                                   )

        # register the account / ensure that it is registered
        if not dbAccountKey.timestamp_last_authenticated:
            do__LetsencryptAccountKey_authenticate(dbSession,
                                                   dbAccountKey,
                                                   account_key_path=tmpfile_account.name,
                                                   )

        # verify each domain
        acme.acme_verify_domains(csr_domains=csr_domains,
                                 account_key_path=tmpfile_account.name,
                                 handle_keyauth_challenge=process_keyauth_challenge,
                                 handle_keyauth_cleanup=process_keyauth_cleanup,
                                 thumbprint=thumbprint,
                                 header=header,
                                 )

        # sign it
        (cert_pem,
         chained_pem,
         chain_url,
         datetime_signed,
         datetime_expires,
         ) = acme.acme_sign_certificate(csr_path=tmpfile_csr.name,
                                        account_key_path=tmpfile_account.name,
                                        header=header,
                                        )
        #
        # end acme-tiny
        # ######################################################################

        # these MUST commit
        with transaction.manager as tx:
            if dbAccountKey not in dbSession:
                dbAccountKey = dbSession.merge(dbAccountKey)
            if dbPrivateKey not in dbSession:
                dbPrivateKey = dbSession.merge(dbPrivateKey)
            if dbLetsencryptCertificateRequest not in dbSession:
                dbLetsencryptCertificateRequest = dbSession.merge(dbLetsencryptCertificateRequest)
            dbLetsencryptServerCertificate = create__LetsencryptServerCertificate(
                dbSession,
                timestamp_signed = datetime_signed,
                timestamp_expires = datetime_expires,
                is_active = True,
                cert_pem = cert_pem,
                chained_pem = chained_pem,
                chain_name = chain_url,
                dbLetsencryptCertificateRequest = dbLetsencryptCertificateRequest,
                dbLetsencryptAccountKey = dbAccountKey,
                dbLetsencryptPrivateKey = dbPrivateKey,
                dbLetsencryptDomains = [v[0] for v in dbDomainObjects.values()],
                letsencrypt_server_certificate_id__renewal_of = letsencrypt_server_certificate_id__renewal_of,
            )

        # merge this back in
        if dbLetsencryptServerCertificate:
            if dbLetsencryptServerCertificate not in dbSession:
                dbLetsencryptServerCertificate = dbSession.merge(dbLetsencryptServerCertificate)
        return dbLetsencryptServerCertificate

    except:
        if dbLetsencryptCertificateRequest:
            if dbLetsencryptCertificateRequest not in dbSession:
                dbLetsencryptCertificateRequest = dbSession.merge(dbLetsencryptCertificateRequest)
                dbLetsencryptCertificateRequest.is_active = False
                dbLetsencryptCertificateRequest.is_error = True
                transaction.manager.commit()
        raise

    finally:

        # cleanup tmpfiles
        for tf in tmpfiles:
            tf.close()

    return


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def create__LetsencryptServerCertificate(
    dbSession,
    timestamp_signed = None,
    timestamp_expires = None,
    is_active = None,
    cert_pem = None,
    chained_pem = None,
    chain_name = None,
    dbLetsencryptCertificateRequest = None,
    dbLetsencryptAccountKey = None,
    dbLetsencryptDomains = None,
    letsencrypt_server_certificate_id__renewal_of = None,

    # only one of these 2
    dbLetsencryptPrivateKey = None,
    privkey_pem = None,
):
    if not any((dbLetsencryptPrivateKey, privkey_pem)) or all((dbLetsencryptPrivateKey, privkey_pem)):
        raise ValueError("create__LetsencryptServerCertificate must accept ONE OF [`dbLetsencryptPrivateKey`, `privkey_pem`]")
    if privkey_pem:
        raise ValueError("need to figure this out; might not need it")

    # we need to figure this out; it's the chained_pem
    # letsencrypt_ca_certificate_id__upchain
    dbCACertificate, _is_created_cert = getcreate__LetsencryptCACertificate__by_pem_text(dbSession, chained_pem, chain_name)
    letsencrypt_ca_certificate_id__upchain = dbCACertificate.id

    cert_pem = cert_utils.cleanup_pem_text(cert_pem)
    try:
        _tmpfileCert = tempfile.NamedTemporaryFile()
        _tmpfileCert.write(cert_pem)
        _tmpfileCert.seek(0)

        # validate
        cert_utils.validate_cert__pem_filepath(_tmpfileCert.name)

        # pull the domains, so we can get the fqdn
        dbFqdnSet, is_created_fqdn = getcreate__LetsencryptUniqueFQDNSet__by_domainObjects(dbSession, dbLetsencryptDomains)

        dbLetsencryptServerCertificate = LetsencryptServerCertificate()
        _certificate_parse_to_record(_tmpfileCert, dbLetsencryptServerCertificate)

        # we don't need these anymore, because we're parsing the cert
        # dbLetsencryptServerCertificate.timestamp_signed = timestamp_signed
        # dbLetsencryptServerCertificate.timestamp_expires = timestamp_signed

        dbLetsencryptServerCertificate.is_active = is_active
        dbLetsencryptServerCertificate.cert_pem = cert_pem
        dbLetsencryptServerCertificate.cert_pem_md5 = utils.md5_text(cert_pem)
        if dbLetsencryptCertificateRequest:
            if dbLetsencryptCertificateRequest not in dbSession:
                dbLetsencryptCertificateRequest = dbSession.merge(dbLetsencryptCertificateRequest)
            dbLetsencryptCertificateRequest.is_active = False
            dbLetsencryptServerCertificate.letsencrypt_certificate_request_id = dbLetsencryptCertificateRequest.id
        dbLetsencryptServerCertificate.letsencrypt_ca_certificate_id__upchain = letsencrypt_ca_certificate_id__upchain
        dbLetsencryptServerCertificate.letsencrypt_server_certificate_id__renewal_of = letsencrypt_server_certificate_id__renewal_of

        # note account/private keys
        dbLetsencryptServerCertificate.letsencrypt_account_key_id = dbLetsencryptAccountKey.id
        dbLetsencryptServerCertificate.letsencrypt_private_key_id__signed_by = dbLetsencryptPrivateKey.id

        # note the fqdn
        dbLetsencryptServerCertificate.letsencrypt_unique_fqdn_set_id = dbFqdnSet.id

        dbSession.add(dbLetsencryptServerCertificate)
        dbSession.flush()

        # increment account/private key counts
        dbLetsencryptAccountKey.count_certificates_issued += 1
        dbLetsencryptPrivateKey.count_certificates_issued += 1
        if not dbLetsencryptAccountKey.timestamp_last_certificate_issue or (dbLetsencryptAccountKey.timestamp_last_certificate_issue < timestamp_signed):
            dbLetsencryptAccountKey.timestamp_last_certificate_issue = timestamp_signed
        if not dbLetsencryptPrivateKey.timestamp_last_certificate_issue or (dbLetsencryptPrivateKey.timestamp_last_certificate_issue < timestamp_signed):
            dbLetsencryptPrivateKey.timestamp_last_certificate_issue = timestamp_signed

        dbSession.flush()

    except:
        raise
    finally:
        _tmpfileCert.close()

    return dbLetsencryptServerCertificate


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def upload__LetsencryptCACertificateBundle__by_pem_text(dbSession, bundle_data):
    results = {}
    for cert_pem in bundle_data.keys():
        if cert_pem[-4:] != '_pem':
            raise ValueError("key does not end in `_pem`")
        cert_base = cert_pem[:-4]
        cert_pem_text = bundle_data[cert_pem]
        cert_name = None
        le_authority_name = None
        is_authority_certificate = None
        is_cross_signed_authority_certificate = None
        for c in letsencrypt_info.CA_CERTS_DATA:
            if cert_base == c['formfield_base']:
                cert_name = c['name']
                if 'le_authority_name' in c:
                    le_authority_name = c['le_authority_name']
                if 'is_authority_certificate' in c:
                    is_authority_certificate = c['is_authority_certificate']
                if 'is_cross_signed_authority_certificate' in c:
                    is_cross_signed_authority_certificate = c['is_cross_signed_authority_certificate']
                break

        dbCACertificate, is_created = getcreate__LetsencryptCACertificate__by_pem_text(
            dbSession,
            cert_pem_text,
            cert_name,
            le_authority_name = None,
            is_authority_certificate = None,
            is_cross_signed_authority_certificate = None,
        )
        if not is_created:
            if dbCACertificate.name in ('unknown', 'manual upload'):
                dbCACertificate.name = cert_name
            if dbCACertificate.le_authority_name is None:
                dbCACertificate.le_authority_name = le_authority_name
            if dbCACertificate.is_authority_certificate is None:
                dbCACertificate.is_authority_certificate = is_authority_certificate
            if dbCACertificate.le_authority_name is None:
                dbCACertificate.is_cross_signed_authority_certificate = is_cross_signed_authority_certificate

        results[cert_pem] = (dbCACertificate, is_created)

    return results


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def ca_certificate_probe(dbSession):
    certs = letsencrypt_info.probe_letsencrypt_certificates()
    certs_discovered = []
    certs_modified = []
    for c in certs:
        _is_created = False
        dbCACertificate = get__LetsencryptCACertificate__by_pem_text(dbSession, c['cert_pem'])
        if not dbCACertificate:
            dbCACertificate, _is_created = getcreate__LetsencryptCACertificate__by_pem_text(dbSession, c['cert_pem'], c['name'])
            if _is_created:
                certs_discovered.append(dbCACertificate)
        if 'is_ca_certificate' in c:
            if dbCACertificate.is_ca_certificate != c['is_ca_certificate']:
                dbCACertificate.is_ca_certificate = c['is_ca_certificate']
                if dbCACertificate not in certs_discovered:
                    certs_modified.append(dbCACertificate)
        else:
            attrs = ('le_authority_name',
                     'is_authority_certificate',
                     'is_cross_signed_authority_certificate',
                     )
            for _k in attrs:
                if getattr(dbCACertificate, _k) is None:
                    setattr(dbCACertificate, _k, c[_k])
                    if dbCACertificate not in certs_discovered:
                        certs_modified.append(dbCACertificate)
    # bookkeeping
    dbEvent = create__LetsencryptOperationsEvent(dbSession,
                                                 LetsencryptOperationsEventType.ca_certificate_probe,
                                                 {'is_certificates_discovered': True if certs_discovered else False,
                                                  'is_certificates_updated': True if certs_modified else False,
                                                  'v': 1,
                                                  }
                                                 )

    return dbEvent


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def operations_update_recents(dbSession):

    # first the single
    # _t_domain = LetsencryptDomain.__table__.alias('domain')
    _q_sub = dbSession.query(LetsencryptServerCertificate.id)\
        .join(LetsencryptUniqueFQDNSet2LetsencryptDomain,
              LetsencryptServerCertificate.letsencrypt_unique_fqdn_set_id == LetsencryptUniqueFQDNSet2LetsencryptDomain.letsencrypt_unique_fqdn_set_id
        )\
        .filter(LetsencryptServerCertificate.is_active == True,  # noqa
                LetsencryptServerCertificate.is_single_domain_cert == True,  # noqa
                LetsencryptUniqueFQDNSet2LetsencryptDomain.letsencrypt_domain_id == LetsencryptDomain.id,
                )\
        .order_by(LetsencryptServerCertificate.timestamp_expires.desc())\
        .limit(1)\
        .subquery()\
        .as_scalar()
    dbSession.execute(LetsencryptDomain.__table__
                      .update()
                      .values(letsencrypt_server_certificate_id__latest_single=_q_sub)
                      )

    # then the multiple
    # _t_domain = LetsencryptDomain.__table__.alias('domain')
    _q_sub = dbSession.query(LetsencryptServerCertificate.id)\
        .join(LetsencryptUniqueFQDNSet2LetsencryptDomain,
              LetsencryptServerCertificate.letsencrypt_unique_fqdn_set_id == LetsencryptUniqueFQDNSet2LetsencryptDomain.letsencrypt_unique_fqdn_set_id
        )\
        .filter(LetsencryptServerCertificate.is_active == True,  # noqa
                LetsencryptServerCertificate.is_single_domain_cert == False,  # noqa
                LetsencryptUniqueFQDNSet2LetsencryptDomain.letsencrypt_domain_id == LetsencryptDomain.id,
                )\
        .order_by(LetsencryptServerCertificate.timestamp_expires.desc())\
        .limit(1)\
        .subquery()\
        .as_scalar()
    dbSession.execute(LetsencryptDomain.__table__
                      .update()
                      .values(letsencrypt_server_certificate_id__latest_multi=_q_sub)
                      )

    # update the count of active certs
    LetsencryptServerCertificate1 = sqlalchemy.orm.aliased(LetsencryptServerCertificate)
    LetsencryptServerCertificate2 = sqlalchemy.orm.aliased(LetsencryptServerCertificate)
    _q_sub = dbSession.query(sqlalchemy.func.count(LetsencryptDomain.id))\
        .outerjoin(LetsencryptServerCertificate1,
                   LetsencryptDomain.letsencrypt_server_certificate_id__latest_single == LetsencryptServerCertificate1.id
                   )\
        .outerjoin(LetsencryptServerCertificate2,
                   LetsencryptDomain.letsencrypt_server_certificate_id__latest_multi == LetsencryptServerCertificate2.id
                   )\
        .filter(sqlalchemy.or_(LetsencryptCACertificate.id == LetsencryptServerCertificate1.letsencrypt_ca_certificate_id__upchain,
                               LetsencryptCACertificate.id == LetsencryptServerCertificate2.letsencrypt_ca_certificate_id__upchain,
                               ),
                )\
        .subquery()\
        .as_scalar()
    dbSession.execute(LetsencryptCACertificate.__table__
                      .update()
                      .values(count_active_certificates=_q_sub)
                      )

    # update the count of active PrivateKeys
    LetsencryptServerCertificate1 = sqlalchemy.orm.aliased(LetsencryptServerCertificate)
    LetsencryptServerCertificate2 = sqlalchemy.orm.aliased(LetsencryptServerCertificate)
    _q_sub = dbSession.query(sqlalchemy.func.count(LetsencryptDomain.id))\
        .outerjoin(LetsencryptServerCertificate1,
                   LetsencryptDomain.letsencrypt_server_certificate_id__latest_single == LetsencryptServerCertificate1.id
                   )\
        .outerjoin(LetsencryptServerCertificate2,
                   LetsencryptDomain.letsencrypt_server_certificate_id__latest_multi == LetsencryptServerCertificate2.id
                   )\
        .filter(sqlalchemy.or_(LetsencryptPrivateKey.id == LetsencryptServerCertificate1.letsencrypt_private_key_id__signed_by,
                               LetsencryptPrivateKey.id == LetsencryptServerCertificate2.letsencrypt_private_key_id__signed_by,
                               ),
                )\
        .subquery()\
        .as_scalar()
    dbSession.execute(LetsencryptPrivateKey.__table__
                      .update()
                      .values(count_active_certificates=_q_sub)
                      )

    # the following works, but this is currently tracked
    if False:
        # update the counts on Account Keys
        _q_sub_req = dbSession.query(sqlalchemy.func.count(LetsencryptCertificateRequest.id))\
            .filter(LetsencryptCertificateRequest.letsencrypt_account_key_id == LetsencryptAccountKey.id,
                    )\
            .subquery()\
            .as_scalar()
        dbSession.execute(LetsencryptAccountKey.__table__
                          .update()
                          .values(count_certificate_requests=_q_sub_req,
                                  # count_certificates_issued=_q_sub_iss,
                                  )
                          )
        # update the counts on Private Keys
        _q_sub_req = dbSession.query(sqlalchemy.func.count(LetsencryptCertificateRequest.id))\
            .filter(LetsencryptCertificateRequest.letsencrypt_private_key_id__signed_by == LetsencryptPrivateKey.id,
                    )\
            .subquery()\
            .as_scalar()
        _q_sub_iss = dbSession.query(sqlalchemy.func.count(LetsencryptServerCertificate.id))\
            .filter(LetsencryptServerCertificate.letsencrypt_private_key_id__signed_by == LetsencryptPrivateKey.id,
                    )\
            .subquery()\
            .as_scalar()

        dbSession.execute(LetsencryptPrivateKey.__table__
                          .update()
                          .values(count_certificate_requests=_q_sub_req,
                                  count_certificates_issued=_q_sub_iss,
                                  )
                          )

    # should we do the timestamps?
    """
    UPDATE letsencrypt_account_key SET timestamp_last_certificate_request = (
    SELECT MAX(timestamp_finished) FROM letsencrypt_certificate_request
    WHERE letsencrypt_certificate_request.letsencrypt_account_key_id = letsencrypt_account_key.id);

    UPDATE letsencrypt_account_key SET timestamp_last_certificate_issue = (
    SELECT MAX(timestamp_signed) FROM letsencrypt_server_certificate
    WHERE letsencrypt_server_certificate.letsencrypt_account_key_id = letsencrypt_account_key.id);

    UPDATE letsencrypt_private_key SET timestamp_last_certificate_request = (
    SELECT MAX(timestamp_finished) FROM letsencrypt_certificate_request
    WHERE letsencrypt_certificate_request.letsencrypt_private_key_id__signed_by = letsencrypt_private_key.id);

    UPDATE letsencrypt_private_key SET timestamp_last_certificate_issue = (
    SELECT MAX(timestamp_signed) FROM letsencrypt_server_certificate
    WHERE letsencrypt_server_certificate.letsencrypt_private_key_id__signed_by = letsencrypt_private_key.id);
    """

    # mark the session changed, but we need to mark the session not scoped session.  ugh.
    # we don't need this if we add the bookkeeping object, but let's just keep this to be safe
    mark_changed(dbSession())

    # bookkeeping
    dbEvent = create__LetsencryptOperationsEvent(dbSession,
                                                 LetsencryptOperationsEventType.update_recents,
                                                 {'v': 1,
                                                  }
                                                 )
    return dbEvent


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def operations_deactivate_expired(dbSession):

    # create an event first
    event_payload_dict = {'count_deactivated': 0,
                          'v': 1,
                          }
    operationsEvent = create__LetsencryptOperationsEvent(dbSession,
                                                         LetsencryptOperationsEventType.deactivate_expired,
                                                         event_payload_dict
                                                         )

    # deactivate expired certificates
    expired_certs = dbSession.query(LetsencryptServerCertificate)\
        .filter(LetsencryptServerCertificate.is_active is True,  # noqa
                LetsencryptServerCertificate.timestamp_expires < datetime.datetime.utcnow(),
                )\
        .all()
    for c in expired_certs:
        c.is_active = False
        dbSession.flush()
        events.Certificate_expired(dbSession, c, operationsEvent=operationsEvent)

    # update the event
    if len(expired_certs):
        event_payload['count_deactivated'] = len(expired_certs)
        operationsEvent.event_payload = json.dumps(event_payload_dict)
        dbSession.flush()
    return operationsEvent


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def operations_deactivate_duplicates(dbSession, ran_operations_update_recents=None):
    """
    this is kind of weird.
    because we have multiple domains, it is hard to figure out which certs we should use
    the simplest approach is this:

    1. cache the most recent certs via `operations_update_recents`
    2. find domains that have multiple active certs
    3. don't turn off any certs that are a latest_single or latest_multi
    """
    raise ValueError("Don't run this. It's not needed anymore")
    if ran_operations_update_recents is not True:
        raise ValueError("MUST run `operations_update_recents` first")

    # bookkeeping
    event_payload_dict = {'count_deactivated': 0,
                          'v': 1,
                          }
    operationsEvent = create__LetsencryptOperationsEvent(
        dbSession,
        LetsencryptOperationsEventType.deactivate_duplicate,
        event_payload_dict,
    )

    _q_ids__latest_single = dbSession.query(LetsencryptDomain.letsencrypt_server_certificate_id__latest_single)\
        .distinct()\
        .filter(LetsencryptDomain.letsencrypt_server_certificate_id__latest_single != None,  # noqa
                )\
        .subquery()
    _q_ids__latest_multi = dbSession.query(LetsencryptDomain.letsencrypt_server_certificate_id__latest_multi)\
        .distinct()\
        .filter(LetsencryptDomain.letsencrypt_server_certificate_id__latest_single != None,  # noqa
                )\
        .subquery()

    # now grab the domains with many certs...
    q_inner = dbSession.query(LetsencryptUniqueFQDNSet2LetsencryptDomain.letsencrypt_domain_id,
                              sqlalchemy.func.count(LetsencryptUniqueFQDNSet2LetsencryptDomain.letsencrypt_domain_id).label('counted'),
                              )\
        .join(LetsencryptServerCertificate,
              LetsencryptUniqueFQDNSet2LetsencryptDomain.letsencrypt_unique_fqdn_set_id == LetsencryptServerCertificate.letsencrypt_unique_fqdn_set_id
              )\
        .filter(LetsencryptServerCertificate.is_active == True,  # noqa
                )\
        .group_by(LetsencryptUniqueFQDNSet2LetsencryptDomain.letsencrypt_domain_id)
    q_inner = q_inner.subquery()
    q_domains = dbSession.query(q_inner)\
        .filter(q_inner.c.counted >= 2)
    result = q_domains.all()
    domain_ids_with_multiple_active_certs = [i.letsencrypt_domain_id for i in result]

    if False:
        _turned_off = []
        for _domain_id in domain_ids_with_multiple_active_certs:
            domain_certs = dbSession.query(LetsencryptServerCertificate)\
                .join(LetsencryptUniqueFQDNSet2LetsencryptDomain,
                      LetsencryptServerCertificate.letsencrypt_unique_fqdn_set_id == LetsencryptUniqueFQDNSet2LetsencryptDomain.letsencrypt_unique_fqdn_set_id,
                      )\
                .filter(LetsencryptServerCertificate.is_active == True,  # noqa
                        LetsencryptUniqueFQDNSet2LetsencryptDomain.letsencrypt_domain_id == _domain_id,
                        LetsencryptServerCertificate.id.notin_(_q_ids__latest_single),
                        LetsencryptServerCertificate.id.notin_(_q_ids__latest_multi),
                        )\
                .order_by(LetsencryptServerCertificate.timestamp_expires.desc())\
                .all()
            if len(domain_certs) > 1:
                for cert in domain_certs[1:]:
                    cert.is_active = False
                    _turned_off.append(cert)
                    events.Certificate_deactivated(dbSession, c, operationsEvent=operationsEvent)

    # update the event
    if len(_turned_off):
        event_payload['count_deactivated'] = len(_turned_off)
        operationsEvent.event_payload = json.dumps(event_payload_dict)
        dbSession.flush()
    return operationsEvent


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def create__LetsencryptOperationsEvent(dbSession, event_type_id, event_payload_dict):
    # bookkeeping
    dbEvent = LetsencryptOperationsEvent()
    dbEvent.letsencrypt_operations_event_type_id = event_type_id
    dbEvent.timestamp_operation = datetime.datetime.utcnow()
    dbEvent.event_payload = json.dumps(event_payload_dict)
    dbSession.add(dbEvent)
    dbSession.flush()
    return dbEvent


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def create__LetsencryptQueueRenewal(dbSession, serverCertificate, letsencrypt_operations_event_id__child_of=None):
    # bookkeeping
    dbQueue = LetsencryptQueueRenewal()
    dbQueue.timestamp_entered = datetime.datetime.utcnow()
    dbQueue.timestamp_processed = None
    dbQueue.letsencrypt_server_certificate_id = serverCertificate.id
    dbQueue.letsencrypt_unique_fqdn_set_id = serverCertificate.letsencrypt_unique_fqdn_set_id
    dbQueue.letsencrypt_operations_event_id__child_of = letsencrypt_operations_event_id__child_of
    dbSession.add(dbQueue)
    dbSession.flush()
    return dbQueue


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def _certificate_parse_to_record(_tmpfileCert, dbCertificate):

    # grab the modulus
    cert_pem_modulus_md5 = cert_utils.modulus_md5_cert__pem_filepath(_tmpfileCert.name)
    dbCertificate.cert_pem_modulus_md5 = cert_pem_modulus_md5

    dbCertificate.timestamp_signed = cert_utils.parse_startdate_cert__pem_filepath(_tmpfileCert.name)
    dbCertificate.timestamp_expires = cert_utils.parse_enddate_cert__pem_filepath(_tmpfileCert.name)
    dbCertificate.cert_subject = cert_utils.cert_single_op__pem_filepath(_tmpfileCert.name, '-subject')
    dbCertificate.cert_subject_hash = cert_utils.cert_single_op__pem_filepath(_tmpfileCert.name, '-subject_hash')
    dbCertificate.cert_issuer = cert_utils.cert_single_op__pem_filepath(_tmpfileCert.name, '-issuer')
    dbCertificate.cert_issuer_hash = cert_utils.cert_single_op__pem_filepath(_tmpfileCert.name, '-issuer_hash')

    return dbCertificate


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def do__LetsencryptAccountKey_authenticate(dbSession, dbLetsencryptAccountKey, account_key_path=None):
    _tmpfile = None
    try:
        if account_key_path is None:
            _tmpfile = tempfile.NamedTemporaryFile()
            _tmpfile.write(dbLetsencryptAccountKey.key_pem)
            _tmpfile.seek(0)
            account_key_path = _tmpfile.name

        # parse account key to get public key
        header, thumbprint = acme.account_key__header_thumbprint(account_key_path=account_key_path, )

        acme.acme_register_account(header,
                                   account_key_path=account_key_path)

        # this would raise if we couldn't authenticate

        dbLetsencryptAccountKey.timestamp_last_authenticated = datetime.datetime.utcnow()
        dbSession.flush()

        return True

    finally:
        if _tmpfile:
            _tmpfile.close()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def queue_domains(dbSession, domain_names):
    results = {d: None for d in domain_names}
    for domain_name in domain_names:
        _exists = get__LetsencryptDomain__by_name(dbSession, domain_name, preload=False)
        if _exists:
            results[domain_name] = 'exists'
        elif not _exists:
            _exists_queue = get__LetsencryptQueueDomain__by_name(dbSession, domain_name)
            if _exists_queue:
                results[domain_name] = 'already_queued'
            elif not _exists_queue:
                dbQueue = LetsencryptQueueDomain()
                dbQueue.domain_name = domain_name
                dbQueue.timestamp_entered = datetime.datetime.utcnow()
                dbSession.add(dbQueue)
                dbSession.flush()
                results[domain_name] = 'queued'
    return results
