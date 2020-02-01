# pyramid
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.renderers import render, render_to_response
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPSeeOther

# stdlib
import datetime
import json

# pypi
import sqlalchemy
import transaction

# localapp
from .. import lib
from ..lib import formhandling
from ..lib.forms import Form_QueueRenewal_mark
from ..lib.handler import Handler, items_per_page
from ...lib import db as lib_db
from ...lib import utils
from ...model import utils as model_utils


# ==============================================================================


class ViewList(Handler):
    """
    note-
    if a renewal fails, the record is marked with the following:
        timestamp_process_attempt = time.time()
        process_result = False
    Records with the above are the failed renewal attempts.

    The record stays active and in the queue, as it may renew later on.
    To be removed, it must suucceed or be explicitly removed from the queue.
    """

    @view_config(
        route_name="admin:queue_renewals", renderer="/admin/queue-renewals.mako"
    )
    @view_config(
        route_name="admin:queue_renewals_paginated",
        renderer="/admin/queue-renewals.mako",
    )
    @view_config(
        route_name="admin:queue_renewals:all", renderer="/admin/queue-renewals.mako"
    )
    @view_config(
        route_name="admin:queue_renewals:all_paginated",
        renderer="/admin/queue-renewals.mako",
    )
    @view_config(
        route_name="admin:queue_renewals:active_failures",
        renderer="/admin/queue-renewals.mako",
    )
    @view_config(
        route_name="admin:queue_renewals:active_failures_paginated",
        renderer="/admin/queue-renewals.mako",
    )
    @view_config(route_name="admin:queue_renewals|json", renderer="json")
    @view_config(route_name="admin:queue_renewals_paginated|json", renderer="json")
    @view_config(route_name="admin:queue_renewals:all|json", renderer="json")
    @view_config(route_name="admin:queue_renewals:all_paginated|json", renderer="json")
    @view_config(
        route_name="admin:queue_renewals:active_failures|json", renderer="json"
    )
    @view_config(
        route_name="admin:queue_renewals:active_failures_paginated|json",
        renderer="json",
    )
    def list(self):
        wants_json = (
            True if self.request.matched_route.name.endswith("|json") else False
        )
        get_kwargs = {}
        url_template = None
        sidenav_option = None
        if self.request.matched_route.name in (
            "admin:queue_renewals",
            "admin:queue_renewals_paginated",
        ):
            get_kwargs["unprocessed_only"] = True
            if wants_json:
                url_template = (
                    "%s/queue-renewals/{0}.json"
                    % self.request.registry.settings["admin_prefix"]
                )
            else:
                url_template = (
                    "%s/queue-renewals/{0}"
                    % self.request.registry.settings["admin_prefix"]
                )
            sidenav_option = "unprocessed"
        elif self.request.matched_route.name in (
            "admin:queue_renewals:all",
            "admin:queue_renewals:all_paginated",
        ):
            if wants_json:
                url_template = (
                    "%s/queue-renewals/{0}.json"
                    % self.request.registry.settings["admin_prefix"]
                )
            else:
                url_template = (
                    "%s/queue-renewals/{0}"
                    % self.request.registry.settings["admin_prefix"]
                )
            sidenav_option = "all"
        elif self.request.matched_route.name in (
            "admin:queue_renewals:active_failures",
            "admin:queue_renewals:active_failures_paginated",
        ):
            get_kwargs["unprocessed_failures_only"] = True
            if wants_json:
                url_template = (
                    "%s/queue-renewals/{0}.json"
                    % self.request.registry.settings["admin_prefix"]
                )
            else:
                url_template = (
                    "%s/queue-renewals/{0}"
                    % self.request.registry.settings["admin_prefix"]
                )
            sidenav_option = "active-failures"

        items_count = lib_db.get.get__SslQueueRenewal__count(
            self.request.api_context, **get_kwargs
        )
        (pager, offset) = self._paginate(items_count, url_template=url_template)
        items_paged = lib_db.get.get__SslQueueRenewal__paginated(
            self.request.api_context, limit=items_per_page, offset=offset, **get_kwargs
        )

        continue_processing = False
        _results = self.request.params.get("results", None)
        if _results:
            try:
                _results = json.loads(_results)
                items_remaining = int(_results.get("count_remaining", 0))
                if items_remaining:
                    continue_processing = True
            except Exception as exc:
                # this could be a json or int() error
                pass
        if wants_json:
            _domains = {d.id: d.as_json for d in items_paged}
            return {
                "SslQueueRenewals": _domains,
                "pagination": {
                    "total_items": items_count,
                    "page": pager.page_num,
                    "page_next": pager.next if pager.has_next else None,
                },
            }
        return {
            "project": "peter_sslers",
            "SslQueueRenewals_count": items_count,
            "SslQueueRenewals": items_paged,
            "sidenav_option": sidenav_option,
            "pager": pager,
            "continue_processing": continue_processing,
        }


class ViewFocus(Handler):
    def _focus(self):
        dbQueueRenewal = lib_db.get.get__SslQueueRenewal__by_id(
            self.request.api_context, self.request.matchdict["id"], load_events=True
        )
        if not dbQueueRenewal:
            raise HTTPNotFound("the item was not found")
        self._focus_item = dbQueueRenewal
        self._focus_url = "%s/queue-renewal/%s" % (
            self.request.admin_url,
            dbQueueRenewal.id,
        )
        return dbQueueRenewal

    @view_config(
        route_name="admin:queue_renewal:focus",
        renderer="/admin/queue-renewal-focus.mako",
    )
    @view_config(route_name="admin:queue_renewal:focus|json", renderer="json")
    def focus(self):
        dbRenewalQueueItem = self._focus()
        wants_json = (
            True if self.request.matched_route.name.endswith("|json") else False
        )
        if wants_json:
            return {"status": "success", "SslQueueRenewal": dbRenewalQueueItem.as_json}
        return {"project": "peter_sslers", "RenewalQueueItem": dbRenewalQueueItem}

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @view_config(route_name="admin:queue_renewal:focus:mark")
    @view_config(route_name="admin:queue_renewal:focus:mark|json", renderer="json")
    def focus_mark(self):
        dbRenewalQueueItem = self._focus()
        if self.request.method == "POST":
            return self._focus_mark__submit(dbRenewalQueueItem)
        return self._focus_mark__print(dbRenewalQueueItem)

    def _focus_mark__print(self, dbRenewalQueueItem):
        wants_json = (
            True if self.request.matched_route.name.endswith("|json") else False
        )
        if wants_json:
            return {
                "instructions": [
                    """curl --form 'action=active' %s/mark.json""" % self._focus_url
                ],
                "form_fields": {"action": "the intended action"},
                "valid_options": {"action": ["cancel"]},
            }
        url_huh = "%s?operation=mark&result=huh" % (self._focus_url)
        return HTTPSeeOther(url_huh)

    def _focus_mark__submit(self, dbRenewalQueueItem):
        wants_json = (
            True if self.request.matched_route.name.endswith("|json") else False
        )
        try:
            (result, formStash) = formhandling.form_validate(
                self.request, schema=Form_QueueRenewal_mark, validate_get=True
            )
            if not result:
                raise formhandling.FormInvalid()

            action = formStash.results["action"]
            event_type = model_utils.SslOperationsEventType.from_string(
                "queue_renewal__mark"
            )
            event_payload_dict = utils.new_event_payload_dict()
            event_payload_dict["ssl_queue_renewal.id"] = dbRenewalQueueItem.id
            event_payload_dict["action"] = formStash.results["action"]

            event_status = False
            if action == "cancel":
                if not dbRenewalQueueItem.is_active:
                    # `formStash.fatal_field()` will raise `FormFieldInvalid(FormInvalid)`
                    formStash.fatal_field(field="action", message="Already cancelled")

                dbRenewalQueueItem.is_active = False
                dbRenewalQueueItem.timestamp_processed = (
                    self.request.api_context.timestamp
                )
                event_status = "queue_renewal__mark__cancelled"
                self.request.api_context.dbSession.flush(objects=[dbRenewalQueueItem])
            else:
                # `formStash.fatal_field()` will raise `FormFieldInvalid(FormInvalid)`
                formStash.fatal_field(field="action", message="invalid action")

            # bookkeeping
            dbOperationsEvent = lib_db.logger.log__SslOperationsEvent(
                self.request.api_context, event_type, event_payload_dict
            )
            lib_db.logger._log_object_event(
                self.request.api_context,
                dbOperationsEvent=dbOperationsEvent,
                event_status_id=model_utils.SslOperationsObjectEventStatus.from_string(
                    event_status
                ),
                dbQueueRenewal=dbRenewalQueueItem,
            )
            if wants_json:
                return {
                    "result": "success",
                    "SslQueueRenewal": dbRenewalQueueItem.as_json,
                }

            url_post_required = "%s?operation=mark&result=success" % (self._focus_url,)
            return HTTPSeeOther(url_post_required)

        except formhandling.FormInvalid as exc:
            if wants_json:
                return {"result": "error", "form_errors": formStash.errors}
            url_failure = "%s?operation=mark&action=%s&result=error&error=%s" % (
                self._focus_url,
                action,
                exc.message,
            )
            raise HTTPSeeOther(url_failure)