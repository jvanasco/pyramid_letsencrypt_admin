<%inherit file="/admin/-site_template.mako"/>
<%namespace name="admin_partials" file="/admin/-partials.mako"/>


<%block name="breadcrumb">
    <ol class="breadcrumb">
        ${request.breadcrumb_prefix|n}
        <li><a href="${admin_prefix}">Admin</a></li>
        <li><a href="${admin_prefix}/certificate-requests">Certificate Requests</a></li>
        <li class="active">Focus [${SslCertificateRequest.id}]</li>
    </ol>
</%block>


<%block name="page_header_col">
    <h2>Certificate Request - Focus</h2>
</%block>


<%block name="page_header_nav">
    <p class="pull-right">
        <a href="${admin_prefix}/certificate-request/${SslCertificateRequest.id}.json" class="btn btn-xs btn-info">
            <span class="glyphicon glyphicon-download-alt" aria-hidden="true"></span>
            .json
        </a>
    </p>
</%block>


<%block name="content_main">
    <div class="row">
        <div class="col-sm-12">
            <table class="table">
                <tr>
                    <th>id</th>
                    <td>
                        <span class="label label-default">
                            ${SslCertificateRequest.id}
                        </span>
                    </td>
                </tr>
                <tr>
                    <th>is_active</th>
                    <td>
                        <span class="label label-${'success' if SslCertificateRequest.is_active else 'warning'}">
                            ${'Active' if SslCertificateRequest.is_active else 'inactive'}
                        </span>
                    </td>
                </tr>
                <tr>
                    <th>is_error</th>
                    <td>
                        <span class="label label-${'danger' if SslCertificateRequest.is_error else 'default'}">
                            ${'Error' if SslCertificateRequest.is_error else 'ok'}
                        </span>
                    </td>
                </tr>
                <tr>
                    <th>certificate_request_source</th>
                    <td>
                        <span class="label label-default">${SslCertificateRequest.certificate_request_source}</span>
                    </td>
                </tr>
                <tr>
                    <th>is issued?</th>
                    <td>
                        % if SslCertificateRequest.server_certificate:
                            <span class="label label-success">Yes</span>&nbsp;
                            <a class="label label-info" href="${admin_prefix}/certificate/${SslCertificateRequest.server_certificate.id}">
                                <span class="glyphicon glyphicon-file" aria-hidden="true"></span>
                                cert-${SslCertificateRequest.server_certificate.id}</a>
                        % else:
                            <span class="label label-default">No</span>
                        % endif
                    </td>
                </tr>
                <tr>
                    <th>is renewal?</th>
                    <td>
                        % if SslCertificateRequest.ssl_server_certificate_id__renewal_of:
                            <span class="label label-success">Yes</span>&nbsp;
                            renewal of Certificate
                            <a class="label label-info" href="${admin_prefix}/certificate/${SslCertificateRequest.ssl_server_certificate_id__renewal_of}">
                                <span class="glyphicon glyphicon-file" aria-hidden="true"></span>
                                cert-${SslCertificateRequest.ssl_server_certificate_id__renewal_of}</a>
                        % else:
                            <span class="label label-default">No</span>
                        % endif
                    </td>
                </tr>
                <tr>
                    <th>ssl_acme_account_key_id</th>
                    <td>
                        % if SslCertificateRequest.ssl_acme_account_key_id:
                            <a class="label label-info" href="${admin_prefix}/account-key/${SslCertificateRequest.ssl_acme_account_key_id}">
                                <span class="glyphicon glyphicon-file" aria-hidden="true"></span>
                                account-${SslCertificateRequest.ssl_acme_account_key_id}</a>
                        % endif
                    </td>
                </tr>
                <tr>
                    <th>ssl_private_key_id__signed_by</th>
                    <td>
                        % if SslCertificateRequest.ssl_private_key_id__signed_by:
                            % if SslCertificateRequest.private_key__signed_by.is_compromised:
                                <a class="label label-danger" href="${admin_prefix}/private-key/${SslCertificateRequest.ssl_private_key_id__signed_by}">
                                    <span class="glyphicon glyphicon-warning-sign" aria-hidden="true"></span>
                                    pkey-${SslCertificateRequest.ssl_private_key_id__signed_by}</a>
                            % else:
                                <a class="label label-info" href="${admin_prefix}/private-key/${SslCertificateRequest.ssl_private_key_id__signed_by}">
                                    <span class="glyphicon glyphicon-file" aria-hidden="true"></span>
                                    pkey-${SslCertificateRequest.ssl_private_key_id__signed_by}</a>
                            % endif
                        % endif
                    </td>
                </tr>
                <tr>
                    <th>unique fqdn set</th>
                    <td>
                        <a class="label label-info" href="${admin_prefix}/unique-fqdn-set/${SslCertificateRequest.ssl_unique_fqdn_set_id}">
                            <span class="glyphicon glyphicon-file" aria-hidden="true"></span>
                            fqdnset-${SslCertificateRequest.ssl_unique_fqdn_set_id}</a>
                    </td>
                </tr>
                <tr>
                    <th>timestamp_started</th>
                    <td>${SslCertificateRequest.timestamp_started}</td>
                </tr>
                <tr>
                    <th>timestamp_finished</th>
                    <td>${SslCertificateRequest.timestamp_finished or ''}</td>
                </tr>
                <tr>
                    <th>csr_pem_md5</th>
                    <td><code>${SslCertificateRequest.csr_pem_md5 or ''}</code></td>
                </tr>
                <tr>
                    <th>csr_pem_modulus_md5</th>
                    <td>
                        % if SslCertificateRequest.csr_pem_modulus_md5:
                            <code>${SslCertificateRequest.csr_pem_modulus_md5}</code>
                            <a
                                class="btn btn-xs btn-info"
                                href="${admin_prefix}/search?${SslCertificateRequest.csr_pem_modulus_search}"
                            >
                                <span class="glyphicon glyphicon-search" aria-hidden="true"></span>
                            </a>
                        % endif
                    </td>
                </tr>
                <tr>
                    <th>csr_pem</th>
                    <td>
                        % if SslCertificateRequest.csr_pem:
                            ## <textarea class="form-control">${SslCertificateRequest.csr_pem}</textarea>
                            <a class="btn btn-xs btn-info" href="${admin_prefix}/certificate-request/${SslCertificateRequest.id}/csr.pem">csr.pem</a>
                            <a class="btn btn-xs btn-info" href="${admin_prefix}/certificate-request/${SslCertificateRequest.id}/csr.pem.txt">csr.pem.txt</a>
                            <a class="btn btn-xs btn-info" href="${admin_prefix}/certificate-request/${SslCertificateRequest.id}/csr.csr">csr.csr [pem format]</a>
                        % else:
                            <em>pem is not tracked</em>
                        % endif
                    </td>
                </tr>
                <tr>
                    <th>domains</th>
                    <td>
                        ${admin_partials.table_SslCertificateRequest2Domain(SslCertificateRequest.to_domains,
                                                                            request_inactive = (False if SslCertificateRequest.is_active else True),
                                                                            perspective='certificate_request')}
                    </td>
                </tr>
            </table>

            % if SslCertificateRequest.is_active and SslCertificateRequest.certificate_request_source_is('acme flow'):
                <a
                    href="${admin_prefix}/certificate-request/${SslCertificateRequest.id}/acme-flow/manage"
                    class="btn btn-info"
                >
                    <span class="glyphicon glyphicon-wrench" aria-hidden="true"></span>
                    Edit Codes
                </a>
                <a
                    href="${admin_prefix}/certificate-request/${SslCertificateRequest.id}/acme-flow/deactivate"
                    class="btn btn-primary"
                >
                    <span class="glyphicon glyphicon-play-circle" aria-hidden="true"></span>
                    deactivate
                </a>
            % endif
        </div>
    </div>
</%block>
