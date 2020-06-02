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
from ..lib.handler import Handler, items_per_page
from ..lib.handler import json_pagination
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
    def list(self):
        items_count = lib_db.get.get__UniqueFQDNSet__count(self.request.api_context)
        if self.request.wants_json:
            (pager, offset) = self._paginate(
                items_count,
                url_template="%s/unique-fqdn-sets/{0}.json"
                % self.request.registry.settings["app_settings"]["admin_prefix"],
            )
        else:
            (pager, offset) = self._paginate(
                items_count,
                url_template="%s/unique-fqdn-sets/{0}"
                % self.request.registry.settings["app_settings"]["admin_prefix"],
            )
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
    def _focus(self):
        dbItem = lib_db.get.get__UniqueFQDNSet__by_id(
            self.request.api_context, self.request.matchdict["id"]
        )
        if not dbItem:
            raise HTTPNotFound("the fqdn set was not found")
        return dbItem

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(
        route_name="admin:unique_fqdn_set:focus",
        renderer="/admin/unique_fqdn_set-focus.mako",
    )
    @view_config(route_name="admin:unique_fqdn_set:focus|json", renderer="json")
    def focus(self):
        dbFqdnSet = self._focus()
        if self.request.wants_json:
            _prefix = "%s/unique-fqdn-set/%s" % (
                self.request.registry.settings["app_settings"]["admin_prefix"],
                dbFqdnSet.id,
            )
            return {"UniqueFQDNSet": dbFqdnSet.as_json}

        return {"project": "peter_sslers", "UniqueFQDNSet": dbFqdnSet}

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(
        route_name="admin:unique_fqdn_set:focus:calendar|json", renderer="json"
    )
    def focus__calendar(self):
        rval = {}
        dbUniqueFQDNSet = self._focus()
        weekly_certs = (
            self.request.api_context.dbSession.query(
                model_utils.year_week(
                    model_objects.ServerCertificate.timestamp_signed
                ).label("week_num"),
                sqlalchemy.func.count(model_objects.ServerCertificate.id),
            )
            .filter(
                model_objects.ServerCertificate.unique_fqdn_set_id == dbUniqueFQDNSet.id
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
        (pager, offset) = self._paginate(
            items_count,
            url_template="%s/unique-fqdn-set/%s/acme-orders/{0}"
            % (
                self.request.registry.settings["app_settings"]["admin_prefix"],
                dbUniqueFQDNSet.id,
            ),
        )
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
        (pager, offset) = self._paginate(
            items_count,
            url_template="%s/unique-fqdn-set/%s/certificate-requests/{0}"
            % (
                self.request.registry.settings["app_settings"]["admin_prefix"],
                dbUniqueFQDNSet.id,
            ),
        )
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
        route_name="admin:unique_fqdn_set:focus:server_certificates",
        renderer="/admin/unique_fqdn_set-focus-server_certificates.mako",
    )
    @view_config(
        route_name="admin:unique_fqdn_set:focus:server_certificates_paginated",
        renderer="/admin/unique_fqdn_set-focus-server_certificates.mako",
    )
    def related__ServerCertificates(self):
        dbUniqueFQDNSet = self._focus()
        items_count = lib_db.get.get__ServerCertificate__by_UniqueFQDNSetId__count(
            self.request.api_context, dbUniqueFQDNSet.id
        )
        (pager, offset) = self._paginate(
            items_count,
            url_template="%s/unique-fqdn-set/%s/server-certificates/{0}"
            % (
                self.request.registry.settings["app_settings"]["admin_prefix"],
                dbUniqueFQDNSet.id,
            ),
        )
        items_paged = lib_db.get.get__ServerCertificate__by_UniqueFQDNSetId__paginated(
            self.request.api_context,
            dbUniqueFQDNSet.id,
            limit=items_per_page,
            offset=offset,
        )
        return {
            "project": "peter_sslers",
            "UniqueFQDNSet": dbUniqueFQDNSet,
            "ServerCertificates_count": items_count,
            "ServerCertificates": items_paged,
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
        (pager, offset) = self._paginate(
            items_count,
            url_template="%s/unique-fqdn-set/%s/queue-certificates/{0}"
            % (
                self.request.registry.settings["app_settings"]["admin_prefix"],
                dbUniqueFQDNSet.id,
            ),
        )
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
