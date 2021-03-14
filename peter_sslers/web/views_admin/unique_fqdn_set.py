# pyramid
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.renderers import render, render_to_response
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPSeeOther

# stdlib
import datetime

# pypi
import sqlalchemy
import transaction

# localapp
from .. import lib
from ..lib.docs import docify
from ..lib.docs import formatted_get_docs
from ..lib.handler import Handler, items_per_page
from ..lib.handler import json_pagination
from ..lib import formhandling
from ..lib.forms import Form_UniqueFQDNSet_modify
from ..lib.forms import Form_UniqueFQDNSet_new
from ...model import utils as model_utils
from ...model import objects as model_objects
from ...lib import db as lib_db
from ...lib import errors
from ...lib import utils


# ==============================================================================


class View_List(Handler):
    @view_config(
        route_name="admin:unique_fqdn_sets", renderer="/admin/unique_fqdn_sets.mako"
    )
    @view_config(
        route_name="admin:unique_fqdn_sets_paginated",
        renderer="/admin/unique_fqdn_sets.mako",
    )
    @view_config(route_name="admin:unique_fqdn_sets|json", renderer="json")
    @view_config(route_name="admin:unique_fqdn_sets_paginated|json", renderer="json")
    @docify(
        {
            "endpoint": "/unique-fqdn-sets.json",
            "section": "unique-fqdn-set",
            "about": """list UniqueFQDNSet(s)""",
            "POST": None,
            "GET": True,
            "example": "curl {ADMIN_PREFIX}/unique-fqdn-sets.json",
        }
    )
    @docify(
        {
            "endpoint": "/unique-fqdn-sets/{PAGE}.json",
            "section": "unique-fqdn-set",
            "example": "curl {ADMIN_PREFIX}/unique-fqdn-sets/1.json",
            "variant_of": "/unique-fqdn-sets.json",
        }
    )
    def list(self):
        items_count = lib_db.get.get__UniqueFQDNSet__count(self.request.api_context)
        url_template = (
            "%s/unique-fqdn-sets/{0}"
            % self.request.registry.settings["app_settings"]["admin_prefix"]
        )
        if self.request.wants_json:
            url_template = "%s.json" % url_template
        (pager, offset) = self._paginate(items_count, url_template=url_template)
        items_paged = lib_db.get.get__UniqueFQDNSet__paginated(
            self.request.api_context,
            limit=items_per_page,
            offset=offset,
            eagerload_web=True,
        )
        if self.request.wants_json:
            _sets = {s.id: s.as_json for s in items_paged}
            return {
                "UniqueFQDNSets": _sets,
                "pagination": json_pagination(items_count, pager),
            }
        return {
            "project": "peter_sslers",
            "UniqueFQDNSets_count": items_count,
            "UniqueFQDNSets": items_paged,
            "pager": pager,
        }


class View_Focus(Handler):
    dbUniqueFQDNSet = None

    def _focus(self):
        if self.dbUniqueFQDNSet is None:
            dbUniqueFQDNSet = lib_db.get.get__UniqueFQDNSet__by_id(
                self.request.api_context, self.request.matchdict["id"]
            )
            if not dbUniqueFQDNSet:
                raise HTTPNotFound("the Unique FQDN Set was not found")
            self.dbUniqueFQDNSet = dbUniqueFQDNSet
            self._focus_item = dbUniqueFQDNSet
            self._focus_url = "%s/unique-fqdn-set/%s" % (
                self.request.registry.settings["app_settings"]["admin_prefix"],
                self.dbUniqueFQDNSet.id,
            )
        return self.dbUniqueFQDNSet

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(
        route_name="admin:unique_fqdn_set:focus",
        renderer="/admin/unique_fqdn_set-focus.mako",
    )
    @view_config(route_name="admin:unique_fqdn_set:focus|json", renderer="json")
    @docify(
        {
            "endpoint": "/unique-fqdn-set/{ID}.json",
            "section": "unique-fqdn-set",
            "about": """unique-fqdn-set focus""",
            "POST": None,
            "GET": True,
            "example": "curl {ADMIN_PREFIX}/unique-fqdn-set/1.json",
        }
    )
    def focus(self):
        dbUniqueFQDNSet = self._focus()
        if self.request.wants_json:
            return {"UniqueFQDNSet": dbUniqueFQDNSet.as_json}

        return {"project": "peter_sslers", "UniqueFQDNSet": dbUniqueFQDNSet}

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(
        route_name="admin:unique_fqdn_set:focus:calendar|json", renderer="json"
    )
    @docify(
        {
            "endpoint": "/unique-fqdn-set/{ID}/calendar.json",
            "section": "unique-fqdn-set",
            "about": """unique-fqdn-set focus: calendar""",
            "POST": None,
            "GET": True,
            "example": "curl {ADMIN_PREFIX}/unique-fqdn-set/1/calendar.json",
        }
    )
    def calendar(self):
        rval = {}
        dbUniqueFQDNSet = self._focus()
        weekly_certs = (
            self.request.api_context.dbSession.query(
                model_utils.year_week(
                    model_objects.CertificateSigned.timestamp_not_before
                ).label("week_num"),
                sqlalchemy.func.count(model_objects.CertificateSigned.id),
            )
            .filter(
                model_objects.CertificateSigned.unique_fqdn_set_id == dbUniqueFQDNSet.id
            )
            .group_by("week_num")
            .order_by(sqlalchemy.asc("week_num"))
            .all()
        )
        rval["issues"] = {}
        for wc in weekly_certs:
            rval["issues"][str(wc[0])] = wc[1]
        return rval

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(route_name="admin:unique_fqdn_set:focus:update_recents", renderer=None)
    @view_config(
        route_name="admin:unique_fqdn_set:focus:update_recents|json", renderer="json"
    )
    @docify(
        {
            "endpoint": "/unique-fqdn-set/{ID}/update-recents.json",
            "section": "unique-fqdn-set",
            "about": """unique-fqdn-set focus: update-recents""",
            "POST": True,
            "GET": None,
            "example": "curl {ADMIN_PREFIX}/unique-fqdn-set/1/update-recents.json",
        }
    )
    def update_recents(self):
        dbUniqueFQDNSet = self._focus()
        if self.request.method != "POST":
            if self.request.wants_json:
                return formatted_get_docs(
                    self, "/unique-fqdn-set/{ID}/update-recents.json"
                )
            return HTTPSeeOther(
                "%s?result=error&operation=update-recents&message=POST+required"
                % (self._focus_url,)
            )
        try:
            operations_event = lib_db.actions.operations_update_recents__domains(
                self.request.api_context,
                dbUniqueFQDNSets=[
                    dbUniqueFQDNSet,
                ],
            )
            if self.request.wants_json:
                return {
                    "result": "success",
                    "UniqueFQDNSet": dbUniqueFQDNSet.as_json,
                }
            return HTTPSeeOther(
                "%s?result=success&operation=update-recents" % (self._focus_url,)
            )

        except Exception as exc:
            raise

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(
        route_name="admin:unique_fqdn_set:focus:acme_orders",
        renderer="/admin/unique_fqdn_set-focus-acme_orders.mako",
    )
    @view_config(
        route_name="admin:unique_fqdn_set:focus:acme_orders_paginated",
        renderer="/admin/unique_fqdn_set-focus-acme_orders.mako",
    )
    def related__AcmeOrders(self):
        dbUniqueFQDNSet = self._focus()
        items_count = lib_db.get.get__AcmeOrder__by_UniqueFQDNSetId__count(
            self.request.api_context, dbUniqueFQDNSet.id
        )
        url_template = "%s/acme-orders/{0}" % self._focus_url
        (pager, offset) = self._paginate(items_count, url_template=url_template)
        items_paged = lib_db.get.get__AcmeOrder__by_UniqueFQDNSetId__paginated(
            self.request.api_context,
            dbUniqueFQDNSet.id,
            limit=items_per_page,
            offset=offset,
        )
        return {
            "project": "peter_sslers",
            "UniqueFQDNSet": dbUniqueFQDNSet,
            "AcmeOrders_count": items_count,
            "AcmeOrders": items_paged,
            "pager": pager,
        }

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(
        route_name="admin:unique_fqdn_set:focus:certificate_requests",
        renderer="/admin/unique_fqdn_set-focus-certificate_requests.mako",
    )
    @view_config(
        route_name="admin:unique_fqdn_set:focus:certificate_requests_paginated",
        renderer="/admin/unique_fqdn_set-focus-certificate_requests.mako",
    )
    def related__CertificateRequests(self):
        dbUniqueFQDNSet = self._focus()
        items_count = lib_db.get.get__CertificateRequest__by_UniqueFQDNSetId__count(
            self.request.api_context, dbUniqueFQDNSet.id
        )
        url_template = "%s/certificate-requests/{0}" % self._focus_url
        (pager, offset) = self._paginate(items_count, url_template=url_template)
        items_paged = lib_db.get.get__CertificateRequest__by_UniqueFQDNSetId__paginated(
            self.request.api_context,
            dbUniqueFQDNSet.id,
            limit=items_per_page,
            offset=offset,
        )
        return {
            "project": "peter_sslers",
            "UniqueFQDNSet": dbUniqueFQDNSet,
            "CertificateRequests_count": items_count,
            "CertificateRequests": items_paged,
            "pager": pager,
        }

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(
        route_name="admin:unique_fqdn_set:focus:certificate_signeds",
        renderer="/admin/unique_fqdn_set-focus-certificate_signeds.mako",
    )
    @view_config(
        route_name="admin:unique_fqdn_set:focus:certificate_signeds_paginated",
        renderer="/admin/unique_fqdn_set-focus-certificate_signeds.mako",
    )
    def related__CertificateSigneds(self):
        dbUniqueFQDNSet = self._focus()
        items_count = lib_db.get.get__CertificateSigned__by_UniqueFQDNSetId__count(
            self.request.api_context, dbUniqueFQDNSet.id
        )
        url_template = "%s/certificate-signeds/{0}" % self._focus_url
        (pager, offset) = self._paginate(items_count, url_template=url_template)
        items_paged = lib_db.get.get__CertificateSigned__by_UniqueFQDNSetId__paginated(
            self.request.api_context,
            dbUniqueFQDNSet.id,
            limit=items_per_page,
            offset=offset,
        )
        return {
            "project": "peter_sslers",
            "UniqueFQDNSet": dbUniqueFQDNSet,
            "CertificateSigneds_count": items_count,
            "CertificateSigneds": items_paged,
            "pager": pager,
        }

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(
        route_name="admin:unique_fqdn_set:focus:queue_certificates",
        renderer="/admin/unique_fqdn_set-focus-queue_certificates.mako",
    )
    @view_config(
        route_name="admin:unique_fqdn_set:focus:queue_certificates_paginated",
        renderer="/admin/unique_fqdn_set-focus-queue_certificates.mako",
    )
    def related__QueueCertificates(self):
        dbUniqueFQDNSet = self._focus()
        items_count = lib_db.get.get__QueueCertificate__by_UniqueFQDNSetId__count(
            self.request.api_context, dbUniqueFQDNSet.id
        )
        url_template = "%s/queue-certificates/{0}" % self._focus_url
        (pager, offset) = self._paginate(items_count, url_template=url_template)
        items_paged = lib_db.get.get__QueueCertificate__by_UniqueFQDNSetId__paginated(
            self.request.api_context,
            dbUniqueFQDNSet.id,
            limit=items_per_page,
            offset=offset,
        )
        return {
            "project": "peter_sslers",
            "UniqueFQDNSet": dbUniqueFQDNSet,
            "QueueCertificates_count": items_count,
            "QueueCertificates": items_paged,
            "pager": pager,
        }

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(
        route_name="admin:unique_fqdn_set:focus:modify",
        renderer="/admin/unique_fqdn_set-focus-modify.mako",
    )
    @view_config(route_name="admin:unique_fqdn_set:focus:modify|json", renderer="json")
    @docify(
        {
            "endpoint": "/queue-domain/{ID}/modify.json",
            "section": "queue-domain",
            "about": """QueueDomain focus: modify""",
            "POST": True,
            "GET": None,
            "example": "curl {ADMIN_PREFIX}/queue-domain/1/modify.json",
            "instructions": [
                """curl --form 'domains_add=[]' --form 'domains_del=[]' {ADMIN_PREFIX}/modify.json"""
            ],
            "form_fields": {
                "domain_names_add": "a comma separated list of domains to add",
                "domain_names_del": "a comma separated list of domains to delete",
            },
        }
    )
    def modify(self):
        if self.request.method != "POST":
            return self._modify__print()
        return self._modify__submit()

    def _modify__print(self):
        """
        shared printing function
        """
        dbUniqueFQDNSet = self._focus()
        if self.request.wants_json:
            return formatted_get_docs(self, "/unique-fqdn-set/{ID}/modify.json")
        params = {
            "project": "peter_sslers",
            "UniqueFQDNSet": dbUniqueFQDNSet,
        }
        return render_to_response(
            "/admin/unique_fqdn_set-focus-modify.mako", params, self.request
        )

    def _modify__submit(self):
        dbUniqueFQDNSet = self._focus()
        try:
            (result, formStash) = formhandling.form_validate(
                self.request,
                schema=Form_UniqueFQDNSet_modify,
                validate_get=False,
            )
            if not result:
                raise formhandling.FormInvalid()

            # localize form values
            domain_names_add = formStash.results["domain_names_add"]
            domain_names_del = formStash.results["domain_names_del"]

            # ensure domain names are submitted
            if not domain_names_add and not domain_names_del:
                # `formStash.fatal_form()` will raise `FormInvalid()`
                formStash.fatal_form(message="no domain names submitted")

            # Pass 1- Validate Input
            # validate the domain names - add:
            try:
                # this function checks the domain names match a simple regex
                domain_names_add = utils.domains_from_string(domain_names_add)
            except ValueError as exc:
                # `formStash.fatal_field()` will raise `FormFieldInvalid(FormInvalid)`
                formStash.fatal_field(
                    field="domain_names_add", message="invalid domain names detected"
                )
            # validate the domain names - del:
            try:
                # this function checks the domain names match a simple regex
                domain_names_del = utils.domains_from_string(domain_names_del)
            except ValueError as exc:
                # `formStash.fatal_field()` will raise `FormFieldInvalid(FormInvalid)`
                formStash.fatal_field(
                    field="domain_names_del", message="invalid domain names detected"
                )

            # Pass 2- Aggregate Input
            # okay, and then again...
            if not domain_names_add and not domain_names_del:
                # `formStash.fatal_form()` will raise `FormInvalid()`
                formStash.fatal_form(message="no valid domain names submitted")

            # any overlap?
            domain_names_add = set(domain_names_add)
            domain_names_del = set(domain_names_del)
            if not domain_names_add.isdisjoint(domain_names_del):
                # `formStash.fatal_form()` will raise `FormInvalid()`
                formStash.fatal_form(
                    message="Identical domain names submitted for add and delete operations",
                )

            # calculate the validity of the new UniqueFQDNSet
            existing_domains = dbUniqueFQDNSet.domains_as_list
            proposed_domains = set(existing_domains)
            proposed_domains.update(domain_names_add)
            proposed_domains.difference_update(domain_names_del)
            proposed_domains = list(proposed_domains)
            if len(proposed_domains) > 100:
                # `formStash.fatal_form()` will raise `FormInvalid()`
                formStash.fatal_form(
                    message="The proposed set contains more than 100 domain names. "
                    "There is a max of 100 domains per certificate.",
                )
            elif len(proposed_domains) < 1:
                # `formStash.fatal_form()` will raise `FormInvalid()`
                formStash.fatal_form(
                    message="The proposed set contains less than 1 domain name.",
                )
            if set(existing_domains) == set(proposed_domains):
                # `formStash.fatal_form()` will raise `FormInvalid()`
                formStash.fatal_form(
                    message="The proposed UniqueFQDNSet is identical to the existing UniqueFQDNSet.",
                )

            # okay, try to add it
            try:
                (
                    dbUniqueFQDNSet,
                    is_created,
                ) = lib_db.getcreate.getcreate__UniqueFQDNSet__by_domains(
                    self.request.api_context,
                    proposed_domains,
                    allow_blocklisted_domains=False,
                )
            except Exception as exc:
                raise

            if self.request.wants_json:
                return {
                    "result": "success",
                    "operation": "modify",
                    "is_created": is_created,
                    "UniqueFQDNSet": dbUniqueFQDNSet.as_json,
                }
            return HTTPSeeOther(
                "%s/unique-fqdn-set/%s?result=success&operation=modify&is_created=%s"
                % (
                    self.request.registry.settings["app_settings"]["admin_prefix"],
                    dbUniqueFQDNSet.id,
                    is_created,
                )
            )

        except formhandling.FormInvalid as exc:
            if self.request.wants_json:
                return {"result": "error", "form_errors": formStash.errors}
            return formhandling.form_reprint(self.request, self._modify__print)


class ViewNew(Handler):
    @view_config(route_name="admin:unique_fqdn_set:new")
    @view_config(route_name="admin:unique_fqdn_set:new|json", renderer="json")
    @docify(
        {
            "endpoint": "/queue-domain/new.json",
            "section": "queue-domain",
            "about": """QueueDomain focus: new""",
            "POST": True,
            "GET": None,
            "example": "curl {ADMIN_PREFIX}/queue-domain/new.json",
            "instructions": [
                """curl --form 'domain_names=domain_names' {ADMIN_PREFIX}/unique-fqdn-set/new.json"""
            ],
            "form_fields": {
                "domain_names": "required; a comma separated list of domain names",
            },
        }
    )
    def new(self):
        if self.request.method == "POST":
            return self._new__submit()
        return self._new__print()

    def _new__print(self):
        if self.request.wants_json:
            return formatted_get_docs(self, "/unique-fqdn-set/new.json")
        return render_to_response(
            "/admin/unique_fqdn_set-new.mako",
            {},
            self.request,
        )

    def _new__submit(self):
        try:
            (result, formStash) = formhandling.form_validate(
                self.request,
                schema=Form_UniqueFQDNSet_new,
                validate_get=False,
            )
            if not result:
                raise formhandling.FormInvalid()

            # localize form values
            domain_names = formStash.results["domain_names"]

            # Pass 1- Validate Input
            try:
                # this function checks the domain names match a simple regex
                domain_names = utils.domains_from_string(domain_names)
            except ValueError as exc:
                # `formStash.fatal_field()` will raise `FormFieldInvalid(FormInvalid)`
                formStash.fatal_field(
                    field="domain_names", message="invalid domain names detected"
                )

            # Pass 2- Aggregate Input
            # okay, and then again...
            if not domain_names:
                # `formStash.fatal_field()` will raise `FormFieldInvalid(FormInvalid)`
                formStash.fatal_field(
                    field="domain_names", message="no valid domain names submitted"
                )
            if len(domain_names) > 100:
                # `formStash.fatal_field()` will raise `FormFieldInvalid(FormInvalid)`
                formStash.fatal_field(
                    field="domain_names", message="more than 100 domain names submitted"
                )

            # okay, try to add it
            try:
                (
                    dbUniqueFQDNSet,
                    is_created,
                ) = lib_db.getcreate.getcreate__UniqueFQDNSet__by_domains(
                    self.request.api_context,
                    domain_names,
                    allow_blocklisted_domains=False,
                )
            except Exception as exc:
                raise

            if self.request.wants_json:
                return {
                    "result": "success",
                    "operation": "new",
                    "is_created": is_created,
                    "UniqueFQDNSet": dbUniqueFQDNSet.as_json,
                }

            return HTTPSeeOther(
                "%s/unique-fqdn-set/%s?result=success&operation=new&is_created=%s"
                % (
                    self.request.registry.settings["app_settings"]["admin_prefix"],
                    dbUniqueFQDNSet.id,
                    is_created,
                )
            )

        except formhandling.FormInvalid as exc:
            if self.request.wants_json:
                return {"result": "error", "form_errors": formStash.errors}
            return formhandling.form_reprint(self.request, self._new__print)
