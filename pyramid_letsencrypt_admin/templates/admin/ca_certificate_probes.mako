<%inherit file="/admin/-site_template.mako"/>
<%namespace name="admin_partials" file="/admin/-partials.mako"/>


<%block name="breadcrumb">
    <ol class="breadcrumb">
        <li><a href="/.well-known/admin">Admin</a></li>
        <li class="active">Certificate Probes</li>
    </ol>
</%block>


<%block name="page_header">
    <h2>Certificate Probes</h2>
</%block>
    

<%block name="content_main">
    <h2>Update</h2>
    <p>
        <form action="/.well-known/admin/ca_certificate_probes/probe" method="POST">
            <input type="submit" class="btn btn-info">Proble for new certificates</span>
            <br/>
            <em>Checks for new certs on the public internet</em>
        </form>
    </p>

    % if LetsencryptCACertificateProbes:
        ${admin_partials.nav_pager(pager)}
        <table class="table table-striped table-condensed">
            <thead>
                <tr>
                    <th>id</th>
                    <th>event timestamp</th>
                    <th>is_certificates_discovered</th>
                    <th>is_certificates_updated</th>
                </tr>
            </thead>
            <tbody>
                % for event in LetsencryptCACertificateProbes:
                    <tr>
                        <td>${event.id}</td>
                        <td><timestamp>${event.timestamp_operation}</timestamp></td>
                        <td>${True if event.is_certificates_discovered else ''}</td>
                        <td>${True if event.is_certificates_updated else ''}</td>
                    </tr>
                % endfor
            </tbody>
        </table>
    % else:
        <em>
            No certificate probes
        </em>
    % endif



</%block>


