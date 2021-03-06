<%inherit file="/admin/-site_template.mako"/>
<%namespace name="admin_partials" file="/admin/-partials.mako"/>


<%block name="breadcrumb">
    <ol class="breadcrumb">
        ${request.breadcrumb_prefix|n}
        <li><a href="${admin_prefix}">Admin</a></li>
        <li><a href="${admin_prefix}/certificate-signeds">CertificateSigneds</a></li>
        <li class="active">Upload</li>
    </ol>
</%block>


<%block name="page_header_col">
    <h2>Upload Certificate</h2>
    <p>
        You can upload existing certificates for management and deployment.
    </p>
</%block>


<%block name="content_main">

    <div class="row">
        <div class="col-sm-6">

            <%! show_text = False %>
            <form
                action="${admin_prefix}/certificate-signed/upload"
                method="POST"
                enctype="multipart/form-data"
            >
                <% form = request.pyramid_formencode_classic.get_form() %>
                ${form.html_error_main_fillable()|n}

                ${admin_partials.formgroup__PrivateKey_file()}
                <hr/>

                ${admin_partials.formgroup__Certificate_file(show_text=show_text)}
                <hr/>

                ${admin_partials.formgroup__CertificateCA_Chain_file(show_text=show_text)}
                <hr/>

                <button type="submit" class="btn btn-primary"><span class="glyphicon glyphicon-upload"></span> Submit</button>

            </form>
        </div>
        <div class="col-sm-6">

            <h2>Why do you need the private key?  That is a security risk!</h2>
                <p>YES! Storing your private key IS a security risk.</p>
                <p>This tool was designed for distributing the ssl certificate chains -- and private keys -- within a secured LAN.</p>
                <p>If you feel uncomfortable with this tool DO NOT USE IT.  This is for advanced deployments.</p>

            <h2>How can I do this from the command line?</h2>

            <p>running locally from a directory that includes letencrypt issued files, you could do the following:</p>

            <p><code>curl --form "private_key_file_pem=@privkey1.pem" --form "certificate_file=@cert1.pem" --form "chain_file=@chain1.pem" ${request.admin_url}/certificate-signed/upload</code></p>

            <p>But instead of that, post to <code>upload.json</code>, which will give you a json parcel in return</p>

            <p><code>curl --form "private_key_file_pem=@privkey1.pem" --form "certificate_file=@cert1.pem" --form "chain_file=@chain1.pem" ${request.admin_url}/certificate-signed/upload.json</code></p>

            <p>The JSON response will have a <code>result</code> attribute that is "success" or "error"; if there is an error, you will see the info in <code>form_errors</code></p>

            <table class="table table-striped table-condensed">
                <tr>
                    <th>valid form</th>
                    <td><code>{"private_key": {"id": 2, "created": false}, "certificate_ca": {"id": 1, "created": false}, "result": "success", "certificate": {"url": "${admin_prefix}/certificate-signed/2", "id": 2, "created": false}}</code></td>
                </tr>
                <tr>
                    <th>valid form</th>
                    <td><code>{"form_errors": {"Error_Main": "There was an error with your form. ", "chain_file": "Missing value"}, "result": "error"}</code></td>
                </tr>
            </table>

            <h2>What do all these mean?</h2>

            <p>
                If you are famiiliar with LetsEncrypt or most other Certificate Authorities
            </p>

            <table class="table table-striped table-condensed">
                <tr>
                    <th>Private Key</th>
                    <td>The private key used to sign requests</td>
                    <td><code>privkey.pem</code></td>
                </tr>
                <tr>
                    <th>Signed Certificate</th>
                    <td>The signed certificate file in PEM format</td>
                    <td><code>cert.pem</code></td>
                </tr>
                <tr>
                    <th>Chain File</th>
                    <td>The upstream chain from the CA</td>
                    <td><code>chain.pem</code></td>
                </tr>
            </table>

            <p>
                Right now this tool only handles Chain files that include a single cert.
                We do not need <code>fullchain.pem</code>, because that is just <code>cert.pem + chain.pem</code>
            </p>

        </div>
    </div>
</%block>
