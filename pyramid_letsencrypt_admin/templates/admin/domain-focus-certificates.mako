<%inherit file="/admin/-site_template.mako"/>
<%namespace name="admin_partials" file="/admin/-partials.mako"/>


<%block name="breadcrumb">
    <ol class="breadcrumb">
        <li><a href="/.well-known/admin">Admin</a></li>
        <li><a href="/.well-known/admin/domains">Domains</a></li>
        <li><a href="/.well-known/admin/domain/${LetsencryptManagedDomain.id}">Focus [${LetsencryptManagedDomain.id}]</a></li>
        <li class="active">Certificates</li>
    </ol>
</%block>


<%block name="page_header">
    <h2>Domain Focus - Certificates</h2>
</%block>

    
<%block name="content_main">


    % if LetsencryptHttpsCertificates:
        ${admin_partials.nav_pager(pager)}
        ${admin_partials.table_certificates__list(LetsencryptHttpsCertificates, show_domains=True)}
    % else:
        No known certificates.
    % endif 


</%block>
