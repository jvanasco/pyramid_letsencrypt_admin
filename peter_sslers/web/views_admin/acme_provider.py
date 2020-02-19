# pyramid
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.renderers import render, render_to_response

# stdlib
import datetime

# pypi
import sqlalchemy

# localapp
from ..lib.handler import Handler
from ..lib.handler import json_pagination
from ...model import utils as model_utils


# ==============================================================================


class ViewAdmin(Handler):
    @view_config(
        route_name="admin:acme_providers", renderer="/admin/acme_providers.mako"
    )
    @view_config(route_name="admin:acme_providers|json", renderer="json")
    def acme_providers(self):
        acmeProviders = list(model_utils.AcmeAccountProvider.registry.values())
        if self.request.wants_json:
            # no pagination
            return {"AcmeProviders": acmeProviders}
        return {"project": "peter_sslers", "AcmeProviders": acmeProviders}

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
