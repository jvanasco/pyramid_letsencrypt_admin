<%inherit file="/admin/-site_template.mako"/>
<%namespace name="admin_partials" file="/admin/-partials.mako"/>


<%block name="breadcrumb">
    <ol class="breadcrumb">
        ${request.breadcrumb_prefix|n}
        <li><a href="${admin_prefix}">Admin</a></li>
        <li><a href="${admin_prefix}/certificate-cas">CertificateCAs</a></li>
        <li class="active">Upload Cert</li>
    </ol>
</%block>


<%block name="page_header_col">
    <h2>CertificateCAs | Upload Cert</h2>
</%block>


<%block name="page_header_nav">
    <p class="pull-right">
        <a href="${admin_prefix}/certificate-ca/upload-cert.json" class="btn btn-xs btn-info">
            <span class="glyphicon glyphicon-upload-alt" aria-hidden="true"></span>
            .json</a>
    </p>
</%block>


<%block name="content_main">

    <div class="row">
        <div class="col-sm-6">

            <%! show_text = False %>

            <form
                action="${admin_prefix}/certificate-ca/upload-cert"
                method="POST"
                enctype="multipart/form-data"
            >
                <% form = request.pyramid_formencode_classic.get_form() %>
                ${form.html_error_main_fillable()|n}

                ${admin_partials.formgroup__CertificateCA_Cert_file(show_text=show_text)}
                <hr/>

                <button type="submit" class="btn btn-primary"><span class="glyphicon glyphicon-upload"></span> Submit</button>

            </form>
        </div>
        <div class="col-sm-6">
            ${admin_partials.info_CertificateCA()}

            <h3>This form is JSON capable</h3>
            <p>
                <code>curl ${request.api_host}${admin_prefix}/certificate-ca/upload-cert.json</code>
            </p>

            <p>
                You can upload a certificate chain on this form: <br/>
                <a  class="btn btn-primary"
                    href="${admin_prefix}/certificate-ca-chain/upload-chain"
                >Upload CertificateCA Chain</a>
            </p>
        </div>
    </div>
</%block>
