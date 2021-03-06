<%inherit file="/admin/-site_template.mako"/>
<%namespace name="admin_partials" file="/admin/-partials.mako"/>


<%block name="breadcrumb">
    <ol class="breadcrumb">
        ${request.breadcrumb_prefix|n}
        <li><a href="${admin_prefix}">Admin</a></li>
        <li><a href="${admin_prefix}/acme-accounts">AcmeAccounts</a></li>
        <li><a href="${admin_prefix}/acme-account/${AcmeAccount.id}">Focus [${AcmeAccount.id}]</a></li>
        <li class="active">Key Change</li>
    </ol>
</%block>


<%block name="page_header_col">
    <h2>AcmeAccounts - Focus - Key Change</h2>
</%block>


<%block name="page_header_nav">
    <p class="pull-right">
        <a href="${admin_prefix}/acme-account/${AcmeAccount.id}/acme-server/key-change.json" class="btn btn-xs btn-warning">
            <span class="glyphicon glyphicon-refresh" aria-hidden="true"></span>
            .json
        </a>
    </p>
</%block>


<%block name="content_main">
    ${admin_partials.handle_querystring_result()}

    <div class="row">
        <div class="col-sm-12">

            <table class="table">
                <thead>
                    <tr>
                        <th colspan="2">
                            Core Details
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <th>id</th>
                        <td>
                            <span class="label label-default">
                                ${AcmeAccount.id}
                            </span>
                        </td>
                    </tr>
                    <tr>
                        <th>source</th>
                        <td>
                            <span class="label label-default">${AcmeAccount.acme_account_key.acme_account_key_source}</span>
                        </td>
                    </tr>
                    <tr>
                        <th>AcmeAccountProvider</th>
                        <td>
                            <a
                                class="label label-info"
                                href="${admin_prefix}/acme-account-providers"
                            >
                                <span class="glyphicon glyphicon-file" aria-hidden="true"></span>
                                AcmeAccountProvider-${AcmeAccount.acme_account_provider_id}
                                [${AcmeAccount.acme_account_provider.name}]
                                (${AcmeAccount.acme_account_provider.url})
                            </a>
                        </td>
                    </tr>
                    <tr>
                        <th>contact</th>
                        <td><code>${AcmeAccount.contact or ''}</code></td>
                    </tr>
                    <tr>
                        <th>key_pem_md5</th>
                        <td><code>${AcmeAccount.acme_account_key.key_pem_md5}</code>
                        </td>
                    </tr>
                    <tr>
                        <th>Key Rollover</th>
                        <td>
                            <form action="${admin_prefix}/acme-account/${AcmeAccount.id}/acme-server/key-change"
                                  method="POST"
                                  id="form-acme_account-key_change"
                                  >
                                <% form = request.pyramid_formencode_classic.get_form() %>
                                ${form.html_error_main_fillable()|n}
                            
                                <p>Rolling over the key will permanently deactivate it on the server, and replace it with a new key that is automatically generated.</p>

                                <div class="form-group">
                                    <label for="key_pem_existing">key pem - existing</label>
                                    <input type="text" name="key_pem_existing" class="form-control" />
                                    <span class="help-inline">Just to be safe, please submit the existing key_pem_md5 or key_pem.</span>
                                </div>
                        
                                <button class="btn btn-warning" type="submit" name="submit" value="submit">
                                    <span class="glyphicon glyphicon-refresh" aria-hidden="true"></span>
                                    Key Change
                                </button>

                            </form>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</%block>
