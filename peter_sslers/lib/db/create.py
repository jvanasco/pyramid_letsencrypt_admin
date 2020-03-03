# logging
import logging

log = logging.getLogger(__name__)

# stdlib
import datetime
import pdb

# pypi
from dateutil import parser as dateutil_parser

# localapp
from .. import cert_utils
from .. import utils
from ...model import utils as model_utils
from ...model import objects as model_objects
from ... import lib  # from . import db?
from ...lib import errors

# local
from .logger import log__OperationsEvent
from .logger import _log_object_event
from .helpers import _certificate_parse_to_record


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def create__AcmeOrderless(
    ctx, domain_names=None,
):
    """
    Create a new AcmeOrderless Tracker
    :param ctx: (required) A :class:`lib.utils.ApiContext` object
    :param domain_names: (required) An iteratble list of domain names

    Handle the DomainNames FIRST.
    We do not want to generate an `AcmeOrderless` if there are no `Domains`.
    """
    # ???: Should the `getcreate` on domains and challenges be wrapped in a transaction?
    domain_names = list(set(domain_names))
    if not domain_names:
        raise ValueError("Did not make a valid set of domain names")

    domain_objects = {
        _domain_name: lib.db.getcreate.getcreate__Domain__by_domainName(
            ctx, _domain_name
        )[0]
        for _domain_name in domain_names
    }

    active_challenges = []
    for (domain_name, dbDomain) in domain_objects.items():
        _active_challenge = lib.db.get.get__AcmeChallenge__by_DomainId__active(
            ctx, dbDomain.id
        )
        if _active_challenge:
            active_challenges.append(_active_challenge)

    if active_challenges:
        raise errors.AcmeDuplicateChallengesExisting(active_challenges)

    dbAcmeOrderless = model_objects.AcmeOrderless()
    dbAcmeOrderless.is_active = True
    dbAcmeOrderless.timestamp_created = ctx.timestamp
    ctx.dbSession.add(dbAcmeOrderless)
    ctx.dbSession.flush(objects=[dbAcmeOrderless])

    for (domain_name, dbDomain) in domain_objects.items():
        dbAcmeChallenge = create__AcmeChallenge(
            ctx, dbAcmeOrderless=dbAcmeOrderless, dbDomain=dbDomain,
        )

    return dbAcmeOrderless


def create__AcmeOrder(
    ctx,
    acme_order_response=None,
    acme_order_type_id=None,
    acme_order_processing_status_id=None,
    acme_order_processing_strategy_id=None,
    is_auto_renew=None,
    order_url=None,
    dbAcmeAccountKey=None,
    dbAcmeOrder_renewal_of=None,
    dbAcmeOrder_retry_of=None,
    dbCertificateRequest=None,
    dbEventLogged=None,
    dbPrivateKey=None,
    dbUniqueFQDNSet=None,
    transaction_commit=None,
):
    """
    Create a new ACME Order

    `PrivateKey` is required so we don't autogenerate keys on failures

    :param ctx: (required) A :class:`lib.utils.ApiContext` object
    :param acme_order_response: (required) dictionary object from the server, representing an ACME payload
    :param acme_order_type_id: (required) What type of order is this? Valid options are in `:class:model.utils.AcmeOrderType`
    :param acme_order_processing_status_id: (required) Valid options are in `:class:model.utils.AcmeOrder_ProcessingStatus`
    :param acme_order_processing_strategy_id: (required) Valid options are in `:class:model.utils.AcmeOrder_ProcessingStrategy`
    :param is_auto_renew: (optional) should this be auto-renewed?
    :param order_url: (required) the url of the object
    :param dbAcmeAccountKey: (required) The :class:`model.objects.AcmeAccountKey` associated with the order
    :param dbAcmeOrder_retry_of: (optional) A :class:`model.objects.AcmeOrder` object
    :param dbAcmeOrder_renewal_of: (optional) A :class:`model.objects.AcmeOrder` object
    :param dbCertificateRequest: (optional) The :class:`model.objects.CertificateRequest` associated with the order
    :param dbPrivateKey: (optional) The :class:`model.objects.PrivateKey` associated with the order
    :param dbUniqueFQDNSet: (required) The :class:`model.objects.UniqueFQDNSet` associated with the order
    :param dbEventLogged: (required) The :class:`model.objects.AcmeEventLog` associated with submitting the order to LetsEncrypt

    :param transaction_commit: (required) Boolean value. required to indicate this persists to the database.
    """
    if not transaction_commit:
        raise ValueError("`create__AcmeOrder` must persist to the database.")

    if acme_order_type_id not in model_utils.AcmeOrderType._mapping:
        raise ValueError("Unsupported `acme_order_type_id`: %s" % acme_order_type_id)

    if acme_order_response is None:
        raise ValueError(
            "`create__AcmeOrder` must be invoked with a `acme_order_response`."
        )

    if not dbPrivateKey:
        raise ValueError("`create__AcmeOrder` must be invoked with a `dbPrivateKey`.")

    if not any((dbCertificateRequest, dbUniqueFQDNSet)):
        raise ValueError(
            "`create__AcmeOrder` must have at least one of (dbCertificateRequest, dbUniqueFQDNSet)."
        )

    if all((dbCertificateRequest, dbUniqueFQDNSet)):
        if dbCertificateRequest.unique_fqdn_set_id != dbUniqueFQDNSet.id:
            raise ValueError(
                "`create__AcmeOrder` mismatch of (dbCertificateRequest, dbUniqueFQDNSet)."
            )

    if dbAcmeOrder_retry_of:
        if dbCertificateRequest:
            if dbAcmeOrder_retry_of.certificate_request != dbCertificateRequest:
                raise ValueError("received conflicting CertificateRequests.")
        else:
            dbCertificateRequest = dbAcmeOrder_retry_of.certificate_request

    # acme_status_order_id = model_utils.Acme_Status_Order.DEFAULT_ID
    acme_status_order_id = model_utils.Acme_Status_Order.from_string(
        acme_order_response["status"]
    )
    finalize_url = acme_order_response.get("finalize")
    timestamp_expires = acme_order_response.get("expires")
    if timestamp_expires:
        timestamp_expires = dateutil_parser.parse(timestamp_expires)
        timestamp_expires = timestamp_expires.replace(tzinfo=None)

    if all((dbAcmeOrder_retry_of, dbAcmeOrder_renewal_of)):
        raise ValueError(
            "`create__AcmeOrder` must be invoked with one or None of (`dbAcmeOrder_retry_of, dbAcmeOrder_renewal_of`)."
        )

    dbAcmeOrder = model_objects.AcmeOrder()
    dbAcmeOrder.is_active = True
    dbAcmeOrder.is_auto_renew = is_auto_renew
    dbAcmeOrder.timestamp_created = ctx.timestamp
    dbAcmeOrder.order_url = order_url
    dbAcmeOrder.acme_order_type_id = acme_order_type_id
    dbAcmeOrder.acme_status_order_id = acme_status_order_id
    dbAcmeOrder.acme_order_processing_status_id = acme_order_processing_status_id
    dbAcmeOrder.acme_order_processing_strategy_id = acme_order_processing_strategy_id
    dbAcmeOrder.acme_account_key_id = dbAcmeAccountKey.id
    dbAcmeOrder.acme_event_log_id = dbEventLogged.id
    dbAcmeOrder.certificate_request_id = (
        dbCertificateRequest.id if dbCertificateRequest else None
    )
    dbAcmeOrder.private_key_id = dbPrivateKey.id
    dbAcmeOrder.unique_fqdn_set_id = dbUniqueFQDNSet.id
    dbAcmeOrder.finalize_url = finalize_url
    dbAcmeOrder.timestamp_expires = timestamp_expires
    dbAcmeOrder.timestamp_updated = datetime.datetime.utcnow()
    if dbAcmeOrder_retry_of:
        dbAcmeOrder.acme_order_id__retry_of = dbAcmeOrder_retry_of.id
    if dbAcmeOrder_renewal_of:
        dbAcmeOrder.acme_order_id__renewal_of = dbAcmeOrder_renewal_of.id

    ctx.dbSession.add(dbAcmeOrder)
    ctx.dbSession.flush(objects=[dbAcmeOrder])

    # then update the event with the order
    dbEventLogged.acme_order_id = dbAcmeOrder.id
    ctx.dbSession.flush(objects=[dbEventLogged])

    # now loop the authorization URLs to create stubs for this order
    for authorization_url in acme_order_response.get("authorizations"):
        (
            dbAuthPlacholder,
            is_auth_created,
        ) = lib.db.getcreate.getcreate__AcmeAuthorizationUrl(
            ctx, authorization_url, dbAcmeOrder
        )

    # persist this to the db
    if transaction_commit:
        ctx.pyramid_transaction_commit()

    return dbAcmeOrder


def create__AcmeAuthorization(*args, **kwargs):
    raise ValueError("use `getcreate__AcmeAuthorization`")


def create__AcmeChallenge(
    ctx,
    dbAcmeOrderless=None,
    dbAcmeAuthorization=None,
    dbDomain=None,
    challenge_url=None,
    token=None,
    keyauthorization=None,
    acme_status_challenge_id=model_utils.Acme_Status_Challenge.DEFAULT_ID,
    is_via_sync=None,
):
    """
    Create a new Challenge
    :param ctx: (required) A :class:`lib.utils.ApiContext` object
    :param dbAcmeOrderless: (optional) The :class:`model.objects.AcmeOrderless`
    :param dbAcmeAuthorization: (optional) The :class:`model.objects.AcmeAuthorization`
    :param dbDomain: (required) The :class:`model.objects.Domain`
    :param challenge_url: (optional) challenge_url token
    :param token: (optional) string token
    :param keyauthorization: (optional) string keyauthorization
    :param acme_status_challenge_id: (optional) An option from :class:`model_utils.Acme_Status_Challenge`.
    :param is_via_sync: (optional) boolean. if True will allow duplicate challenges as one is on the server
    
    """
    if not any((dbAcmeOrderless, dbAcmeAuthorization)) or all(
        (dbAcmeOrderless, dbAcmeAuthorization)
    ):
        raise ValueError(
            "must be invoked with one and only one of `dbAcmeOrderless` or `dbAcmeAuthorization`"
        )
    if not dbDomain:
        raise ValueError("must be invoked with `dbDomain`")

    if dbAcmeOrderless:
        orderless_domain_ids = [c.domain_id for c in dbAcmeOrderless.acme_challenges]
        if dbDomain in orderless_domain_ids:
            raise errors.AcmeDuplicateOrderlessDomain(
                "Domain `%s` already in this AcmeOrderless." % c.domain.domain_name
            )

    _active_challenge = lib.db.get.get__AcmeChallenge__by_DomainId__active(
        ctx, dbDomain.id
    )
    if _active_challenge:
        if not is_via_sync:
            raise errors.AcmeDuplicateChallenge(_active_challenge)
        else:
            print("need to handle this")

    dbAcmeChallenge = model_objects.AcmeChallenge()
    if dbAcmeOrderless:
        dbAcmeChallenge.acme_orderless_id = dbAcmeOrderless.id
    elif dbAcmeAuthorization:
        dbAcmeChallenge.acme_authorization_id = dbAcmeAuthorization.id
    dbAcmeChallenge.timestamp_created = ctx.timestamp
    dbAcmeChallenge.domain_id = dbDomain.id
    dbAcmeChallenge.acme_challenge_type_id = model_utils.AcmeChallengeType.from_string(
        "http-01"
    )
    dbAcmeChallenge.acme_status_challenge_id = acme_status_challenge_id
    dbAcmeChallenge.token = token
    dbAcmeChallenge.keyauthorization = keyauthorization
    dbAcmeChallenge.challenge_url = challenge_url

    ctx.dbSession.add(dbAcmeChallenge)
    ctx.dbSession.flush(objects=[dbAcmeChallenge])

    return dbAcmeChallenge


def create__AcmeChallengePoll(ctx, dbAcmeChallenge=None, remote_ip_address=None):
    """
    Create a new AcmeChallengePoll - this is a log

    :param ctx: (required) A :class:`lib.utils.ApiContext` object
    :param dbAcmeChallenge: (required) The challenge which was polled
    :param remote_ip_address: (required) The remote ip address (string)
    """
    remote_ip_address_id = None
    if remote_ip_address:
        (dbRemoteIpAddress, _created) = lib.db.getcreate.getcreate__RemoteIpAddress(
            ctx, remote_ip_address
        )
        remote_ip_address_id = dbRemoteIpAddress.id

    dbAcmeChallengePoll = model_objects.AcmeChallengePoll()
    dbAcmeChallengePoll.acme_challenge_id = dbAcmeChallenge.id
    dbAcmeChallengePoll.timestamp_polled = ctx.timestamp
    dbAcmeChallengePoll.remote_ip_address_id = remote_ip_address_id
    ctx.dbSession.add(dbAcmeChallengePoll)
    ctx.dbSession.flush(objects=[dbAcmeChallengePoll])
    return dbAcmeChallengePoll


def create__AcmeChallengeUnknownPoll(
    ctx, domain=None, challenge=None, remote_ip_address=None
):
    """
    Create a new AcmeChallengeUnknownPoll - this is an unknown polling

    :param ctx: (required) A :class:`lib.utils.ApiContext` object
    :param domain: (required) domain (string)
    :param challenge: (required) challenge (string)
    :param remote_ip_address: (required) remote_ip_address (string)
    """
    remote_ip_address_id = None
    if remote_ip_address:
        (dbRemoteIpAddress, _created) = lib.db.getcreate.getcreate__RemoteIpAddress(
            ctx, remote_ip_address
        )
        remote_ip_address_id = dbRemoteIpAddress.id

    dbAcmeChallengeUnknownPoll = model_objects.AcmeChallengeUnknownPoll()
    dbAcmeChallengeUnknownPoll.domain = domain
    dbAcmeChallengeUnknownPoll.challenge = challenge
    dbAcmeChallengeUnknownPoll.timestamp_polled = ctx.timestamp
    dbAcmeChallengeUnknownPoll.remote_ip_address_id = remote_ip_address_id
    ctx.dbSession.add(dbAcmeChallengeUnknownPoll)
    ctx.dbSession.flush(objects=[dbAcmeChallengeUnknownPoll])
    return dbAcmeChallengeUnknownPoll


def create__CertificateRequest(
    ctx,
    csr_pem=None,
    certificate_request_source_id=None,
    dbPrivateKey=None,
    dbServerCertificate__issued=None,
    domain_names=None,
):
    """
    Create a new Certificate Signing Request (CSR)

    :param ctx: (required) A :class:`lib.utils.ApiContext` object
    :param csr_pem: (required) A Certificate Signing Request with PEM formatting
    :param certificate_request_source_id: (required) What is the source of this? Valid options are in `:class:model.utils.CertificateRequestSource`
    :param dbPrivateKey: (required) Private Key used to sign the CSR

    :param dbServerCertificate__issued: (optional) a `model_objects.ServerCertificate`
    :param domain_names: (required) A list of domain names
    """
    if (
        certificate_request_source_id
        not in model_utils.CertificateRequestSource._mapping
    ):
        raise ValueError(
            "Unsupported `certificate_request_source_id`: %s"
            % certificate_request_source_id
        )

    _event_type_id = None
    if certificate_request_source_id == model_utils.CertificateRequestSource.IMPORTED:
        _event_type_id = model_utils.OperationsEventType.from_string(
            "CertificateRequest__new__imported"
        )
    elif (
        certificate_request_source_id == model_utils.CertificateRequestSource.ACME_ORDER
    ):
        _event_type_id = model_utils.OperationsEventType.from_string(
            "CertificateRequest__new__acme_order"
        )
    else:
        raise ValueError(
            "Unsupported `certificate_request_source_id`: %s"
            % certificate_request_source_id
        )

    if domain_names is None:
        raise ValueError("Must submit `domain_names` for creation")

    if dbPrivateKey is None:
        raise ValueError("Must submit `dbPrivateKey` for creation")

    if csr_pem is None:
        raise ValueError("Must submit a valid `csr_pem`")
    csr_pem = cert_utils.cleanup_pem_text(csr_pem)

    # scoping
    csr_domain_names = None
    csr_pem_md5 = None
    csr_pem_modulus_md5 = None

    event_payload_dict = utils.new_event_payload_dict()
    dbOperationsEvent = log__OperationsEvent(ctx, _event_type_id)

    _tmpfile = None
    try:
        # store the csr_text in a tmpfile
        _tmpfile = cert_utils.new_pem_tempfile(csr_pem)

        # validate
        cert_utils.validate_csr__pem_filepath(_tmpfile.name)

        _csr_domain_names = cert_utils.parse_csr_domains(
            csr_path=_tmpfile.name, submitted_domain_names=domain_names
        )
        csr_domain_names = utils.domains_from_list(_csr_domain_names)
        if len(csr_domain_names) != len(_csr_domain_names):
            raise ValueError(
                "One or more of the domain names in the CSR are not allowed (%s)"
                % _csr_domain_names
            )
        if not csr_domain_names:
            raise ValueError(
                "Must submit `csr_pem` that contains `domain_names` (found None)"
            )
        if set(csr_domain_names) != set(domain_names):
            raise ValueError(
                "received different values for `domain_names` than exist in the CSR"
            )

        # calculate the md5
        csr_pem_md5 = utils.md5_text(csr_pem)
        # grab the modulus
        csr_pem_modulus_md5 = cert_utils.modulus_md5_csr__pem_filepath(_tmpfile.name)
    finally:
        _tmpfile.close()

    # ensure the domains are registered into our system
    domain_objects = {
        _domain_name: lib.db.getcreate.getcreate__Domain__by_domainName(
            ctx, _domain_name
        )[0]
        for _domain_name in domain_names
    }
    # we'll use this tuple in a bit...
    # getcreate__Domain__by_domainName returns a tuple of (domainObject, is_created)
    (
        dbUniqueFQDNSet,
        is_created_fqdn,
    ) = lib.db.getcreate.getcreate__UniqueFQDNSet__by_domainObjects(
        ctx, domain_objects.values()
    )

    # build the cert
    dbCertificateRequest = model_objects.CertificateRequest()
    dbCertificateRequest.timestamp_created = ctx.timestamp
    dbCertificateRequest.certificate_request_source_id = certificate_request_source_id
    dbCertificateRequest.csr_pem = csr_pem
    dbCertificateRequest.csr_pem_md5 = csr_pem_md5  # computed in initial block
    dbCertificateRequest.csr_pem_modulus_md5 = (
        csr_pem_modulus_md5  # computed in initial block
    )
    dbCertificateRequest.operations_event_id__created = dbOperationsEvent.id
    dbCertificateRequest.private_key_id = dbPrivateKey.id
    dbCertificateRequest.unique_fqdn_set_id = dbUniqueFQDNSet.id

    ctx.dbSession.add(dbCertificateRequest)
    ctx.dbSession.flush(objects=[dbCertificateRequest])

    event_payload_dict["certificate_request.id"] = dbCertificateRequest.id
    dbOperationsEvent.set_event_payload(event_payload_dict)
    ctx.dbSession.flush(objects=[dbOperationsEvent])

    _log_object_event(
        ctx,
        dbOperationsEvent=dbOperationsEvent,
        event_status_id=model_utils.OperationsObjectEventStatus.from_string(
            "CertificateRequest__insert"
        ),
        dbCertificateRequest=dbCertificateRequest,
    )

    #
    # increment private key counts
    #
    dbPrivateKey.count_certificate_requests += 1
    if not dbPrivateKey.timestamp_last_certificate_request or (
        dbPrivateKey.timestamp_last_certificate_request < ctx.timestamp
    ):
        dbPrivateKey.timestamp_last_certificate_request = ctx.timestamp
    ctx.dbSession.flush(objects=[dbPrivateKey])

    return dbCertificateRequest


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def create__PrivateKey(
    ctx, bits=None, private_key_source_id=None, is_autogenerated=None
):
    """
    Generates a new :class:`model.objects.PrivateKey` for the datastore

    :param ctx: (required) A :class:`lib.utils.ApiContext` object
    :param int bits: (required) how many bits for the PrivateKey
    :param private_key_source_id: (required) A string matching a source in A :class:`lib.utils.PrivateKeySource`
    :param boolean is_autogenerated: (optional) True if this is autogenerated by the caledar
    """
    key_pem = cert_utils.new_private_key(bits=bits)
    dbPrivateKey, _is_created = lib.db.getcreate.getcreate__PrivateKey__by_pem_text(
        ctx,
        key_pem,
        private_key_source_id=private_key_source_id,
        is_autogenerated_key=is_autogenerated,
    )
    return dbPrivateKey


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def create__ServerCertificate(
    ctx,
    cert_pem=None,
    dbAcmeOrder=None,
    dbCACertificate=None,
    ca_chain_pem=None,
    ca_chain_name=None,
    dbCertificateRequest=None,
    dbPrivateKey=None,
    is_active=None,
    cert_domains_expected=None,
    dbDomains=None,
):
    """
    Create a new ServerCertificate

    :param ctx: (required) A :class:`lib.utils.ApiContext` object
    :param cert_pem: (required) The certificate in PEM encoding

    :param dbAcmeOrder: (optional) The :class:`model.objects.AcmeOrder` the certificate was generated through.
        if provivded, do not submit `dbCertificateRequest` or `dbPrivateKey`
    :param dbCACertificate: (optional) The :class:`model.objects.CACertificate` that signed this certificate
        if not provided, please submit `ca_chain_pem` and `ca_chain_name`
    :param ca_chain_pem: (optional) The CA Certificate's PEM if :param:`dbCACertificate` is not provided
    :param ca_chain_name: (optional) The CA Certificate's Name if :param:`dbCACertificate` is not provided

    :param dbCertificateRequest: (optional) The :class:`model.objects.CertificateRequest` the certificate was generated through.
        if provivded, do not submit `dbAcmeOrder`
    :param dbPrivateKey: (optional) The :class:`model.objects.PrivateKey` that signed the certificate, if no `dbAcmeOrder` is provided
    :param is_active: (optional) default `None`  do not activate a certificate when uploading unless specified.

    :param cert_domains_expected: (required) a list of domains in the cert we expect to see
    """
    if not any((dbAcmeOrder, dbPrivateKey)):
        raise ValueError(
            "create__ServerCertificate must be provided with `dbPrivateKey` or `dbAcmeOrder`"
        )
    if not any((dbAcmeOrder, dbCertificateRequest)):
        raise ValueError(
            "create__ServerCertificate must be provided with `dbCertificateRequest` or `dbAcmeOrder`"
        )

    dbAcmeAccountKey = None
    if dbAcmeOrder:
        dbAcmeAccountKey = dbAcmeOrder.acme_account_key
        dbUniqueFqdnSet = dbAcmeOrder.unique_fqdn_set
        if dbCertificateRequest:
            if dbCertificateRequest != dbAcmeOrder.certificate_request:
                raise ValueError(
                    "create__ServerCertificate was with `dbCertificateRequest` and a conflicting `dbAcmeOrder`"
                )
        else:
            dbCertificateRequest = dbAcmeOrder.certificate_request
        if dbPrivateKey:
            if dbPrivateKey != dbAcmeOrder.private_key:
                raise ValueError(
                    "create__ServerCertificate was with `dbPrivateKey` and a conflicting `dbAcmeOrder`"
                )
        else:
            dbPrivateKey = dbAcmeOrder.certificate_request.private_key

    if dbCACertificate:
        if any((ca_chain_pem, ca_chain_name)):
            raise ValueError(
                "do not submit `ca_chain_pem, ca_chain_name` with a `dbCACertificate`"
            )
    else:
        if not all((ca_chain_pem, ca_chain_name)):
            raise ValueError(
                "must submit `ca_chain_pem, ca_chain_name` with a `dbCACertificate`"
            )
        # we need to figure this out; it's the ca_chain_pem
        # ca_certificate_id__upchain
        (
            dbCACertificate,
            _is_created__CACertificate,
        ) = lib.db.getcreate.getcreate__CACertificate__by_pem_text(
            ctx, ca_chain_pem, ca_chain_name
        )
        if not dbCACertificate:
            raise ValueError("Could not create a `dbCACertificate`")
    ca_certificate_id__upchain = dbCACertificate.id

    # build or interpret this
    unique_fqdn_set_id = None
    if dbAcmeOrder:
        unique_fqdn_set_id = dbAcmeOrder.unique_fqdn_set_id
    elif dbCertificateRequest:
        unique_fqdn_set_id = dbCertificateRequest.unique_fqdn_set_id
    else:
        # the domains can be generated but is there a system that handles this now?
        raise ValueError("how did this happen?")

    # bookkeeping
    event_payload_dict = utils.new_event_payload_dict()
    dbOperationsEvent = log__OperationsEvent(
        ctx, model_utils.OperationsEventType.from_string("ServerCertificate__insert")
    )

    _tmpfileCert = None
    try:

        # cleanup the cert_pem
        cert_pem = cert_utils.cleanup_pem_text(cert_pem)
        _tmpfileCert = cert_utils.new_pem_tempfile(cert_pem)

        # validate
        cert_utils.validate_cert__pem_filepath(_tmpfileCert.name)

        # validate the domains!
        # let's make sure have the right domains in the cert!!
        # this only happens on development during tests when we use a single cert
        # for all requests...
        # so we don't need to handle this or save it
        cert_domains = cert_utils.parse_cert_domains(_tmpfileCert.name)
        if set(cert_domains_expected) != set(cert_domains):
            # if not acme_v2.TESTING_ENVIRONMENT:
            log.error("set(cert_domains_expected) != set(cert_domains)")
            log.error(cert_domains_expected)
            log.error(cert_domains)
            raise ValueError(
                "Certificate Domains do not match the expected ones! this should never happen!"
            )

        # ok, now pull the dates off the cert

        dbServerCertificate = model_objects.ServerCertificate()
        dbServerCertificate.cert_pem = cert_pem
        dbServerCertificate.cert_pem_md5 = utils.md5_text(cert_pem)
        dbServerCertificate.is_active = is_active
        dbServerCertificate.unique_fqdn_set_id = unique_fqdn_set_id
        dbServerCertificate.private_key_id = dbPrivateKey.id
        dbServerCertificate.operations_event_id__created = dbOperationsEvent.id
        """
        The following are set by `_certificate_parse_to_record`
            :attr:`model.utils.ServerCertificate.cert_pem_modulus_md5`
            :attr:`model.utils.ServerCertificate.timestamp_signed`
            :attr:`model.utils.ServerCertificate.timestamp_expires`
            :attr:`model.utils.ServerCertificate.cert_subject`
            :attr:`model.utils.ServerCertificate.cert_subject_hash`
            :attr:`model.utils.ServerCertificate.cert_issuer`
            :attr:`model.utils.ServerCertificate.cert_issuer_hash`
        """
        _certificate_parse_to_record(_tmpfileCert, dbServerCertificate)
        if dbCertificateRequest:
            dbServerCertificate.certificate_request_id = dbCertificateRequest.id
        dbServerCertificate.ca_certificate_id__upchain = ca_certificate_id__upchain

        ctx.dbSession.add(dbServerCertificate)
        ctx.dbSession.flush(objects=[dbServerCertificate])

        # increment account/private key counts
        dbPrivateKey.count_certificates_issued += 1
        if not dbPrivateKey.timestamp_last_certificate_issue or (
            dbPrivateKey.timestamp_last_certificate_issue
            < dbServerCertificate.timestamp_signed
        ):
            dbPrivateKey.timestamp_last_certificate_issue = (
                dbServerCertificate.timestamp_signed
            )
        if dbAcmeAccountKey:
            dbAcmeAccountKey.count_certificates_issued += 1
            if not dbAcmeAccountKey.timestamp_last_certificate_issue or (
                dbAcmeAccountKey.timestamp_last_certificate_issue
                < dbServerCertificate.timestamp_signed
            ):
                dbAcmeAccountKey.timestamp_last_certificate_issue = (
                    dbServerCertificate.timestamp_signed
                )

        event_payload_dict["server_certificate.id"] = dbServerCertificate.id
        dbOperationsEvent.set_event_payload(event_payload_dict)
        ctx.dbSession.flush(objects=[dbOperationsEvent])

        _log_object_event(
            ctx,
            dbOperationsEvent=dbOperationsEvent,
            event_status_id=model_utils.OperationsObjectEventStatus.from_string(
                "ServerCertificate__insert"
            ),
            dbServerCertificate=dbServerCertificate,
        )

        # final, just to be safe
        ctx.dbSession.flush()

    except Exception as exc:
        raise
    finally:
        if _tmpfileCert:
            _tmpfileCert.close()

    return dbServerCertificate


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def create__QueueCertificate(
    ctx,
    dbAcmeAccountKey=None,
    dbPrivateKey=None,
    dbAcmeOrder=None,
    dbServerCertificate=None,
    dbUniqueFQDNSet=None,
):
    """
    Queues an item for renewal

    This must happen within the context other events

    :param ctx: (required) A :class:`lib.utils.ApiContext` object
    :param dbAcmeAccountKey: (required) A :class:`model.objects.AcmeAccountKey` object
    :param dbPrivateKey: (required) A :class:`model.objects.PrivateKey` object

    :param dbAcmeOrder: (optional) A :class:`model.objects.AcmeOrder` object
    :param dbServerCertificate: (optional) A :class:`model.objects.ServerCertificate` object
    :param dbUniqueFQDNSet: (optional) A :class:`model.objects.UniqueFQDNSet` object

    one and only one of (dbAcmeOrder, dbServerCertificate, dbUniqueFQDNSet) should be supplied
    
    
    :returns :class:`model.objects.QueueCertificate`

    """
    if not all((dbAcmeAccountKey, dbPrivateKey)):
        raise ValueError("must supply both `dbAcmeAccountKey` and `dbPrivateKey`")

    if sum(bool(i) for i in (dbAcmeOrder, dbServerCertificate, dbUniqueFQDNSet,)) != 1:
        raise ValueError(
            "Provide one and only one of (`dbAcmeOrder, dbServerCertificate, dbUniqueFQDNSet`)"
        )

    # what are we renewing?
    unique_fqdn_set_id = None
    if dbAcmeOrder:
        unique_fqdn_set_id = dbAcmeOrder.unique_fqdn_set_id
    elif dbServerCertificate:
        unique_fqdn_set_id = dbServerCertificate.unique_fqdn_set_id
    elif dbUniqueFQDNSet:
        unique_fqdn_set_id = dbUniqueFQDNSet.id

    # bookkeeping
    event_payload_dict = utils.new_event_payload_dict()
    dbOperationsEvent = log__OperationsEvent(
        ctx, model_utils.OperationsEventType.from_string("QueueCertificate__insert")
    )

    dbQueueCertificate = model_objects.QueueCertificate()
    dbQueueCertificate.timestamp_entered = ctx.timestamp
    dbQueueCertificate.timestamp_processed = None
    dbQueueCertificate.operations_event_id__created = dbOperationsEvent.id

    # core elements
    dbQueueCertificate.acme_account_key_id = dbAcmeAccountKey.id
    dbQueueCertificate.private_key_id = dbPrivateKey.id
    dbQueueCertificate.unique_fqdn_set_id = unique_fqdn_set_id
    # the source elements
    dbQueueCertificate.acme_order_id__source = dbAcmeOrder.id if dbAcmeOrder else None
    dbQueueCertificate.server_certificate_id__source = (
        dbServerCertificate.id if dbServerCertificate else None
    )
    dbQueueCertificate.unique_fqdn_set_id__source = (
        dbUniqueFQDNSet.id if dbUniqueFQDNSet else None
    )

    ctx.dbSession.add(dbQueueCertificate)
    ctx.dbSession.flush(objects=[dbQueueCertificate])

    # more bookkeeping!
    event_payload_dict["queue_certificate.id"] = dbQueueCertificate.id
    dbOperationsEvent.set_event_payload(event_payload_dict)
    ctx.dbSession.flush(objects=[dbOperationsEvent])
    _log_object_event(
        ctx,
        dbOperationsEvent=dbOperationsEvent,
        event_status_id=model_utils.OperationsObjectEventStatus.from_string(
            "QueueCertificate__insert"
        ),
        dbQueueCertificate=dbQueueCertificate,
    )

    return dbQueueCertificate


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


__all__ = (
    "create__CertificateRequest",
    "create__ServerCertificate",
    "create__PrivateKey",
    "create__QueueCertificate",
)
