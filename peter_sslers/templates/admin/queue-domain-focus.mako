<%inherit file="/admin/-site_template.mako"/>
<%namespace name="admin_partials" file="/admin/-partials.mako"/>


<%block name="breadcrumb">
    <ol class="breadcrumb">
        <li><a href="${admin_prefix}">Admin</a></li>
        <li><a href="${admin_prefix}/queue-domains">Domains Queue</a></li>
        <li class="active">Focus [${QueueDomainItem.id}]</li>
    </ol>
</%block>


<%block name="page_header">
    <h2>Domains Queue | Focus</h2>
</%block>


<%block name="content_main">
    <table class="table">
        <tr>
            <th>id</th>
            <td>
                <span class="label label-default">
                    ${QueueDomainItem.id}
                </span>
            </td>
        </tr>
        <tr>
            <th>domain_name</th>
            <td>
                <code>
                    ${QueueDomainItem.domain_name}
                </code>
            </td>
        </tr>
        <tr>
            <th>timestamp_entered</th>
            <td>
                <timestamp>${QueueDomainItem.timestamp_entered or ''}</timestamp>
            </td>
        </tr>
        <tr>
            <th>timestamp_processed</th>
            <td>
                <timestamp>${QueueDomainItem.timestamp_processed or ''}</timestamp>
            </td>
        </tr>
        <tr>
            <th>domain?</th>
            <td>
                % if QueueDomainItem.ssl_domain_id:
                    <a class="label label-info" href="${admin_prefix}/domain/${QueueDomainItem.ssl_domain_id}">
                        <span class="glyphicon glyphicon-file" aria-hidden="true"></span>
                        ${QueueDomainItem.ssl_domain_id}
                    </a>
                % endif
            </td>
        </tr>
        <tr>
            <th>operations event?</th>
            <td>
               % if False and QueueDomainItem.operations_event:
                    <table class="table table-striped table-condensed">
                        <tr>
                            <th>event type</th>
                            <td>
                                <span class="label label-info">${QueueDomainItem.operations_event.event_type_text}</span>
                            </td>
                        </tr>
                        <tr>
                            <th>timestamp_event</th>
                            <td>
                                <timestamp>${QueueDomainItem.operations_event.timestamp_event or ''}</timestamp>
                            </td>
                        </tr>
                    </table>
               % endif
            </td>
        </tr>
    </table>
    <hr/>

    <h4>Operation Object Events</h4>
    ${admin_partials.table_SslOperationsObjectEvents(QueueDomainItem.operations_object_events, table_context='domain')}
</%block>
