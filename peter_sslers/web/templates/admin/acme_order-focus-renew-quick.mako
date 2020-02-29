<%inherit file="/admin/-site_template.mako"/>
<%namespace name="admin_partials" file="/admin/-partials.mako"/>


<%block name="breadcrumb">
    <ol class="breadcrumb">
        ${request.breadcrumb_prefix|n}
        <li><a href="${admin_prefix}">Admin</a></li>
        <li><a href="${admin_prefix}/acme-orders">AcmeOrder</a></li>
        <li><a href="${admin_prefix}/acme-order/${AcmeOrder.id}">Focus [${AcmeOrder.id}]</a></li>
        <li class="active">Renew Quick</li>
    </ol>
</%block>


<%block name="page_header_col">
    <h2>ACME Order - Focus - Renew Quick</h2>
    <p>${request.text_library.info_AcmeOrders[1]}</p>

    ${admin_partials.standard_error_display()}
</%block>


<%block name="page_header_nav">
    <p class="pull-right">
        <a href="${admin_prefix}/acme-order/${AcmeOrder.id}.json" class="btn btn-xs btn-info">
            <span class="glyphicon glyphicon-download-alt" aria-hidden="true"></span>
            .json
        </a>
    </p>
</%block>


<%block name="content_main">
    ${admin_partials.handle_querystring_result()}
    <div class="row">
        <div class="col-sm-12">

            <h4>Renew the following?</h4>
            <table class="table table-striped table-condensed">
                <tbody>
                    <tr>
                        <th>id</th>
                        <td>
                            <span class="label label-default">
                                <span class="glyphicon glyphicon-file" aria-hidden="true"></span>
                                ${AcmeOrder.id}
                            </span>
                        </td>
                        <td></td>
                    </tr>
                    <tr>
                        <th>acme_account_key_id</th>
                        <td>
                            <a
                                class="label label-info"
                                href="${admin_prefix}/acme-account-key/${AcmeOrder.acme_account_key_id}"
                            >
                                <span class="glyphicon glyphicon-file" aria-hidden="true"></span>
                                AcmeAccountKey-${AcmeOrder.acme_account_key_id}
                            </a>
                        </td>
                        <td><code>${AcmeOrder.acme_account_key.key_pem_sample}</code></td>
                    </tr>
                    <tr>
                        <th>private_key_id</th>
                        <td>
                            <a
                                class="label label-info"
                                href="${admin_prefix}/private-key/${AcmeOrder.private_key_id}"
                            >
                                <span class="glyphicon glyphicon-file" aria-hidden="true"></span>
                                PrivateKey-${AcmeOrder.private_key_id}
                            </a>
                        </td>
                        <td><code>${AcmeOrder.private_key.key_pem_sample}</code></td>
                    </tr>
                    <tr>
                        <th>unique_fqdn_set_id</th>
                        <td>
                            <a
                                class="label label-info"
                                href="${admin_prefix}/unique-fqdn-set/${AcmeOrder.unique_fqdn_set_id}"
                            >
                                <span class="glyphicon glyphicon-file" aria-hidden="true"></span>
                                UniqueFQDNSet-${AcmeOrder.unique_fqdn_set_id}
                            </a>
                        </td>
                        <td>
                            <code>${', '.join(AcmeOrder.domains_as_list)}</code>
                        </td>
                    </tr>
                    <tr>
                        <th></th>
                        <td>
                            <form action="${admin_prefix}/acme-order/${AcmeOrder.id}/renew/quick" method="POST" style="display:inline;">
                                <button class="btn btn-xs btn-primary" type="submit">
                                    <span class="glyphicon glyphicon-repeat" aria-hidden="true"></span>
                                    Renew!
                                </button>
                            </form>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</%block>
