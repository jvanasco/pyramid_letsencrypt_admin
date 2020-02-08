# pyramid
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.renderers import render, render_to_response
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPSeeOther

# stdlib
import json

# pypi
import sqlalchemy

# localapp
from .. import lib
from ..lib import formhandling
from ..lib import form_utils as form_utils
from ..lib import text as lib_text
from ..lib.handler import Handler, items_per_page
from ...lib import acme_v2
from ...lib import cert_utils
from ...lib import db as lib_db
from ...lib import errors
from ...lib import utils
from ...model import utils as model_utils


# ==============================================================================


class ViewAdmin_List(Handler):

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(
        route_name="admin:acme_authorizations",
        renderer="/admin/acme_authorizations.mako",
    )
    @view_config(
        route_name="admin:acme_authorizations_paginated",
        renderer="/admin/acme_authorizations.mako",
    )
    def list(self):
        items_count = lib_db.get.get__AcmeAuthorization__count(self.request.api_context)
        (pager, offset) = self._paginate(
            items_count,
            url_template="%s/acme-authorizations/{0}"
            % self.request.registry.settings["admin_prefix"],
        )
        items_paged = lib_db.get.get__AcmeAuthorization__paginated(
            self.request.api_context, limit=items_per_page, offset=offset
        )
        return {
            "project": "peter_sslers",
            "AcmeAuthorizations_count": items_count,
            "AcmeAuthorizations": items_paged,
            "pager": pager,
        }


class ViewAdmin_Focus(Handler):
    def _focus(self, eagerload_web=False):
        dbAcmeAuthorization = lib_db.get.get__AcmeAuthorization__by_id(
            self.request.api_context,
            self.request.matchdict["id"],
            eagerload_web=eagerload_web,
        )
        if not dbAcmeAuthorization:
            raise HTTPNotFound("the authorization was not found")
        self._focus_url = "%s/acme-authorization/%s" % (
            self.request.admin_url,
            dbAcmeAuthorization.id,
        )
        return dbAcmeAuthorization

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(
        route_name="admin:acme_authorization:focus",
        renderer="/admin/acme_authorization-focus.mako",
    )
    def focus(self):
        dbAcmeAuthorization = self._focus(eagerload_web=True)
        return {"project": "peter_sslers", "AcmeAuthorization": dbAcmeAuthorization}

    @view_config(
        route_name="admin:acme_authorization:focus:orders",
        renderer="/admin/acme_authorization-focus-orders.mako",
    )
    @view_config(
        route_name="admin:acme_authorization:focus:orders_paginated",
        renderer="/admin/acme_authorization-focus-orders.mako",
    )
    def orders(self):
        dbAcmeAuthorization = self._focus(eagerload_web=True)
        items_count = lib_db.get.get__AcmeOrders__by_AcmeAuthorization__count(
            self.request.api_context, dbAcmeAuthorization.id
        )
        (pager, offset) = self._paginate(
            items_count,
            url_template="%s/acme-challenge-unknown-polls/{0}"
            % self.request.registry.settings["admin_prefix"],
        )
        items_paged = lib_db.get.get__AcmeOrders__by_AcmeAuthorization__paginated(
            self.request.api_context,
            dbAcmeAuthorization.id,
            limit=items_per_page,
            offset=offset,
        )
        return {
            "project": "peter_sslers",
            "AcmeAuthorization": dbAcmeAuthorization,
            "AcmeOrders_count": items_count,
            "AcmeOrders": items_paged,
            "pager": pager,
        }