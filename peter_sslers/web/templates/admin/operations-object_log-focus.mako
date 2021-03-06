<%inherit file="/admin/-site_template.mako"/>
<%namespace name="admin_partials" file="/admin/-partials.mako"/>


<%block name="breadcrumb">
    <ol class="breadcrumb">
        ${request.breadcrumb_prefix|n}
        <li><a href="${admin_prefix}">Admin</a></li>
        <li><a href="${admin_prefix}/operations/object-log">Operations Object-Events</a></li>
        <li class="active">Focus</li>
    </ol>
</%block>


<%block name="page_header_col">
    <h2>Operations Object Events</h2>
    ${admin_partials.handle_querystring_result()}
</%block>


<%block name="content_main">
    <div class="row">
        <div class="col-sm-9">
            <table class="table table-striped table-condensed">
                <tr>
                    <th>id</th>
                    <td><span class="label label-default">${OperationsObjectEvent.id}</span></td>
                </tr>
                <tr>
                    <th>event status</th>
                    <td><span class="label label-default">${OperationsObjectEvent.event_status_text}</span></td>
                </tr>
                <tr>
                    <th>operations event</th>
                    <td>
                            <a  href="${admin_prefix}/operations/log/item/${OperationsObjectEvent.operations_event_id}"
                                class="label label-info"
                            >
                                <span class="glyphicon glyphicon-file" aria-hidden="true"></span>
                                ${OperationsObjectEvent.operations_event_id}
                            </a>
                    </td>
                </tr>
                <tr>
                    <th>timestamp</th>
                    <td><timestamp>${OperationsObjectEvent.operations_event.timestamp_event}</timestamp></td>
                </tr>
                <tr>
                    <th>object data</th>
                    <td>
                        ${admin_partials.object_event__object(OperationsObjectEvent)}
                    </td>
                </tr>
            </table>

        </div>
    </div>
</%block>
