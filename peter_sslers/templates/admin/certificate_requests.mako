<%inherit file="/admin/-site_template.mako"/>
<%namespace name="admin_partials" file="/admin/-partials.mako"/>


<%block name="breadcrumb">
    <ol class="breadcrumb">
        <li>Peter SSLers</li>
        <li><a href="${admin_prefix}">Admin</a></li>
        <li>Certificate Requests</li>
    </ol>
</%block>


<%block name="page_header_col">
    <h2>Certificate Requests</h2>
    ${admin_partials.standard_error_display(has_message=True)}
</%block>


<%block name="content_main">
    <div class="row">
        <div class="col-sm-12">
            % if SslCertificateRequests:
                ${admin_partials.nav_pagination(pager)}
                ${admin_partials.table_certificate_requests__list(SslCertificateRequests, show_domains=True, show_certificate=True)}
            % else:
                <em>
                    No Certificate Requests
                </em>
            % endif
        </div>
    </div>
</%block>
