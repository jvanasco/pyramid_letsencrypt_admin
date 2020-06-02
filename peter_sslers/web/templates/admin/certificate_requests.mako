<%inherit file="/admin/-site_template.mako"/>
<%namespace name="admin_partials" file="/admin/-partials.mako"/>


<%block name="breadcrumb">
    <ol class="breadcrumb">
        ${request.breadcrumb_prefix|n}
        <li><a href="${admin_prefix}">Admin</a></li>
        <li>Certificate Requests</li>
    </ol>
</%block>


<%block name="page_header_col">
    <h2>Certificate Requests</h2>
</%block>


<%block name="page_header_nav">
    <p class="pull-right">
        <a href="${admin_prefix}/certificate-requests.json" class="btn btn-xs btn-info">
            <span class="glyphicon glyphicon-download-alt" aria-hidden="true"></span>
            .json
        </a>
    </p>
</%block>


<%block name="content_main">
    ${admin_partials.handle_querystring_result(expect_message=True)}

    <div class="row">
        <div class="col-sm-12">
            % if CertificateRequests:
                ${admin_partials.nav_pagination(pager)}
                ${admin_partials.table_CertificateRequests(CertificateRequests, perspective='CertificateRequest')}
            % else:
                <em>
                    No Certificate Requests
                </em>
            % endif
        </div>
    </div>
</%block>
