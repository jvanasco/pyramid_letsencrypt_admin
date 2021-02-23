# ==============================================================================


json_docs_post_only = {
    "instructions": [
        "HTTP POST required",
    ],
    "form_fields": None,
}


api_endpoints = {
    "/api/certificate-ca/letsencrypt-sync.json": {
        "endpoint": "/api/certificate-ca/letsencrypt-sync.json",
        "about": """download from the LetsEncrypt website""",
        "POST": True,
        "GET": False,
        "args": None,
        "POST-button": True,
    },
    "/api/deactivate-expired.json": {
        "endpoint": "/api/deactivate-expired.json",
        "about": """deactivates expired certificates; runs update-recents""",
        "POST": True,
        "GET": False,
        "args": None,
        "POST-button": True,
    },
    "/api/domain/enable": {
        "endpoint": "/api/domain/enable",
        "about": """Enables domain(s) for management. Currently this proxies calls to `/admin/queue-domains`""",
        "POST": True,
        "GET": False,
        "args": {
            "domain_names": "A comma (,) separated list of domain names",
        },
    },
    "/api/domain/disable": {
        "endpoint": "/api/domain/disable",
        "about": """Disables domain(s) for management""",
        "POST": True,
        "GET": False,
        "args": {
            "domain_names": "A comma (,) separated list of domain names",
        },
    },
    "/api/domain/certificate-if-needed": {
        "endpoint": "/api/domain/certificate-if-needed",
        "about": """Initiates a new certificate if needed. full control of acme-order properties""",
        "POST": True,
        "GET": False,
        "args": {
            "domain_name": "A single",
        },
    },
    "/api/domain/autocert.json": {
        "endpoint": "/api/domain/autocert.json",
        "about": """Initiates a new certificate if needed. only accepts a domain name, uses system defaults""",
        "POST": True,
        "GET": False,
        "GET-SELF-DOCUMENTING": True,
        "GET-button": "/api/domain/autocert",  # set to html, not json
        "args": {
            "domain_name": "A single",
        },
    },
    "/api/redis/prime.json": {
        "endpoint": "/api/redis/prime.json",
        "about": """Primes the Redis cache""",
        "POST": True,
        "GET": False,
        "args": None,
    },
    "/api/update-recents.json": {
        "endpoint": "/api/update-recents.json",
        "about": """updates the db to list the most recent cert for each domain""",
        "POST": True,
        "GET": False,
        "args": None,
        "GET-button": True,
    },
    "/api/nginx/cache-flush.json": {
        "endpoint": "/api/nginx/cache-flush.json",
        "about": """Flushes the Nginx cache. This will make background requests to configured Nginx servers, instructing them to flush their cache. """,
        "POST": True,
        "GET": False,
        "args": None,
    },
    "/api/nginx/status.json": {
        "endpoint": "/api/nginx/status.json",
        "about": """Checks Nginx servers for status via background requests""",
        "POST": True,
        "GET": False,
        "args": None,
    },
    "/api/queue-certificates/update.json": {
        "endpoint": "/api/queue-certificates/update.json",
        "about": """Updates the certificates queue by inspecting active certificates for pending expiries.""",
        "POST": True,
        "GET": False,
        "args": None,
    },
}

json_capable = {
    "/acme-accounts.json": {
        "endpoint": "/acme-accounts.json",
        "section": "acme-account",
        "about": """list AcmeAccounts""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/acme-accounts.json",
    },
    "/acme-accounts/{PAGE}.json": {
        "endpoint": "/acme-accounts/{PAGE}.json",
        "section": "acme-account",
        "about": """list AcmeAccounts, paginated""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/acme-accounts/1.json",
    },
    "/acme-account/{ID}.json": {
        "endpoint": "/acme-account/{ID}.json",
        "section": "acme-account",
        "about": """AcmeAccount record""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/acme-account/1.json",
    },
    "/acme-account/{ID}/config.json": {
        "endpoint": "/acme-account/{ID}/config.json",
        "section": "acme-account",
        "about": """config info for an AcmeAccount""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/acme-account/1/config.json",
    },
    "/acme-account/{ID}/parse.json": {
        "endpoint": "/acme-account/{ID}/parse.json",
        "section": "acme-account",
        "about": """parse an AcmeAccount key""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/acme-account/1/parse.json",
    },
    "/acme-account/{ID}/key.key": {
        "endpoint": "/acme-account/{ID}/key.key",
        "section": "acme-account",
        "about": """AcmeAccount's key as der""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/acme-account/1/key.key",
    },
    "/acme-account/{ID}/key.pem": {
        "endpoint": "/acme-account/{ID}/key.pem",
        "section": "acme-account",
        "about": """key as pem""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/acme-account/1/key.pem",
    },
    "/acme-account/{ID}/key.pem.txt": {
        "endpoint": "/acme-account/{ID}/key.pem.txt",
        "section": "acme-account",
        "about": """key as pem/txt""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/acme-account/1/key.pem.txt",
    },
    "/acme-account/upload.json": {
        "endpoint": "/acme-account/upload.json",
        "section": "acme-account",
        "about": """Upload an account-key""",
        "POST": True,
        "GET": None,
        "GET-SELF-DOCUMENTING": True,
        "args": None,
        "examples": [
            "curl --form 'account_key_file_pem=@key.pem' --form 'acme_account_provider_id=1' {ADMIN_PREFIX}/acme-account/upload.json",
            "curl --form 'account_key_file_le_meta=@meta.json' 'account_key_file_le_pkey=@private_key.json' 'account_key_file_le_reg=@regr.json' {ADMIN_PREFIX}/acme-account/upload.json",
        ],
    },
    "/acme-account/{ID}/acme-server/authenticate.json": {
        "endpoint": "/acme-account/{ID}/acme-server/authenticate.json",
        "section": "acme-account",
        "about": """authenticate the key against the provider's new-reg endpoint""",
        "POST": True,
        "GET": None,
        "GET-SELF-DOCUMENTING": True,
        "args": None,
        "examples": [
            "curl http://127.0.0.1:7201/.well-known/admin/acme-account/1/acme-server/authenticate.json",
            "curl -X POST http://127.0.0.1:7201/.well-known/admin/acme-account/1/acme-server/authenticate.json",
        ],
    },
    "/acme-account/{ID}/acme-server/deactivate-pending-authorizations.json": {
        "endpoint": "/acme-account/{ID}/acme-server/deactivate-pending-authorizations.json",
        "section": "acme-account",
        "about": """deactivate pending authorizations on the acme server, must supply the authorization_ids.""",
        "POST": True,
        "GET": None,
        "GET-SELF-DOCUMENTING": True,
        "args": None,
        "examples": [
            "curl http://127.0.0.1:7201/.well-known/admin/acme-account/1/acme-server/deactivate-pending-authorizations.json",
            "curl --form 'acme_authorization_id=1' --form 'acme_authorization_id=2'  http://127.0.0.1:7201/.well-known/admin/acme-account/1/acme-server/deactivate-pending-authorizations.json",
        ],
    },
    "/acme-account/{ID}/mark.json": {
        "endpoint": "/acme-account/{ID}/mark.json",
        "section": "acme-account",
        "about": """mark the key""",
        "POST": True,
        "GET": None,
        "GET-SELF-DOCUMENTING": True,
        "args": None,
        "example": "curl --form 'action=active' http://127.0.0.1:7201/.well-known/admin/acme-account/1/mark.json",
    },
    "/acme-account-providers.json": {
        "endpoint": "/acme-account-providers.json",
        "section": "acme-account-provider",
        "about": """list acme-account-providers""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/acme-account-providers.json",
    },
    "/acme-challenge/{ID}.json": {
        "endpoint": "/acme-challenge/{ID}.json",
        "section": "acme-challenge",
        "about": """view an acme challenge""",
        "POST": None,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/acme-challenge/{ID}.json",
    },
    "/acme-order/{ID}.json": {
        "endpoint": "/acme-order/{ID}.json",
        "section": "acme-order",
        "about": """view an acme order""",
        "POST": None,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/acme-order/{ID}.json",
    },
    "/acme-order/new/freeform.json": {
        "endpoint": "/acme-order/new/freeform.json",
        "section": "acme-order",
        "about": """create a new acme order""",
        "POST": None,
        "GET": True,
        "GET-SELF-DOCUMENTING": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/acme-order/{ID}.json",
    },
    "/acme-orderless/new.json": {
        "endpoint": "/acme-orderless/new.json",
        "section": "acme-orderless",
        "about": """create a new acme-orderless""",
        "POST": True,
        "GET": None,
        "GET-SELF-DOCUMENTING": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/acme-orderless/new.json",
    },
    "/acme-authorization/{ID}.json": {
        "endpoint": "/acme-authorization/{ID}.json",
        "section": "acme-authorization",
        "about": """view a acme-authorization""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/acme-authorization/{ID}.json",
    },
    "/certificate-cas.json": {
        "endpoint": "/certificate-cas.json",
        "section": "certificate-ca",
        "about": """list certificate-cas""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-cas.json",
    },
    "/certificate-cas/{PAGE}.json": {
        "endpoint": "/certificate-cas/{PAGE}.json",
        "section": "certificate-ca",
        "about": """list certificate-cas, paginated""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-cas/1.json",
    },
    "/certificate-ca/{ID}.json": {
        "endpoint": "/certificate-ca/{ID}.json",
        "section": "certificate-ca",
        "about": """parse certificate""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-ca/1.json",
    },
    "/certificate-ca/{ID}/parse.json": {
        "endpoint": "/certificate-ca/{ID}/parse.json",
        "section": "certificate-ca",
        "about": """parse certificate""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-ca/1/parse.json",
    },
    "/certificate-cas/{ID}/chain.pem": {
        "endpoint": "/certificate-cas/{ID}/chain.pem",
        "section": "certificate-ca",
        "about": """cert as pem""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-ca/1/chain.pem",
    },
    "/certificate-cas/{ID}/chain.pem.txt": {
        "endpoint": "/certificate-cas/{ID}/chain.pem.txt",
        "section": "certificate-ca",
        "about": """cert as pem.txt""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-ca/1/chain.pem.txt",
    },
    "/certificate-cas/{ID}/chain.cer": {
        "endpoint": "/certificate-cas/{ID}/chain.cer",
        "section": "certificate-ca",
        "about": """cert as cer""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-ca/1/chain.cer",
    },
    "/certificate-cas/{ID}/chain.crt": {
        "endpoint": "/certificate-cas/{ID}/chain.crt",
        "section": "certificate-ca",
        "about": """cert as crt""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-ca/1/chain.crt",
    },
    "/certificate-cas/{ID}/chain.der": {
        "endpoint": "/certificate-cas/{ID}/chain.der",
        "section": "certificate-ca",
        "about": """cert as der""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-ca/1/chain.der",
    },
    "/certificate-ca/upload.json": {
        "endpoint": "/certificate-ca/upload.json",
        "section": "certificate-ca",
        "about": """Upload an authority certificate""",
        "POST": True,
        "GET": None,
        "GET-SELF-DOCUMENTING": True,
        "args": None,
        "examples": [
            "curl {ADMIN_PREFIX}/certificate-ca/upload.json",
            "curl --form 'chain_file=@chain1.pem' --form {ADMIN_PREFIX}/certificate-ca/upload.json",
        ],
    },
    "/certificate-signeds.json": {
        "endpoint": "/certificate-signeds.json",
        "section": "certificate-signed",
        "about": """list certificates""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-signeds.json",
    },
    "/certificate-signeds/{PAGE}.json": {
        "endpoint": "/certificate-signeds/{PAGE}.json",
        "section": "certificate-signed",
        "about": """list certificates, paginated""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-signeds/1.json",
    },
    "/certificate-signeds/expiring.json": {
        "endpoint": "/certificate-signeds/expiring.json",
        "section": "certificate-signed",
        "about": """list certificates. expiring.""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-signeds/expiring.json",
    },
    "/certificate-signeds/expiring/{PAGE}.json": {
        "endpoint": "/certificate-signeds/expiring/{PAGE}.json",
        "section": "certificate-signed",
        "about": """list certificates, paginated. expiring.""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-signeds/expiring/1.json",
    },
    "/certificate-signed/{ID}.json": {
        "endpoint": "/certificate-signed/{ID}.json",
        "section": "certificate-signed",
        "about": """certficate as json""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-signed/1.json",
    },
    "/certificate-signed/{ID}/config.json": {
        "endpoint": "/certificate-signed/{ID}/config.json",
        "section": "certificate-signed",
        "about": """config info for a certficate""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-signed/1/config.json",
    },
    "/certificate-signed/{ID}/parse.json": {
        "endpoint": "/certificate-signed/{ID}/parse.json",
        "section": "certificate-signed",
        "about": """parse a certficate""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-signed/1/parse.json",
    },
    "/certificate-signed/{ID}/nginx-cache-expire.json": {
        "endpoint": "/certificate-signed/{ID}/nginx-cache-expire.json",
        "section": "certificate-signed",
        "about": """send reset to Nginx""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-signed/1/nginx-cache-expire.json",
    },
    "/certificate-signed/{ID}/renew/quick.json": {
        "endpoint": "/certificate-signed/{ID}/renew/quick.json",
        "section": "certificate-signed",
        "about": """renewal - quick""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-signed/1/renew/quick.json",
    },
    "/certificate-signed/{ID}/renew/custom.json": {
        "endpoint": "/certificate-signed/{ID}/renew/custom.json",
        "section": "certificate-signed",
        "about": """custom renewal""",
        "POST": True,
        "GET": None,
        "GET-SELF-DOCUMENTING": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/certificate-signed/1/renew/custom.json",
    },
    "/certificate-signed/{ID}/mark.json": {
        "endpoint": "/certificate-signed/{ID}/mark.json",
        "section": "certificate-signed",
        "about": """mark a certficate""",
        "POST": True,
        "GET": None,
        "GET-SELF-DOCUMENTING": True,
        "args": None,
        "examples": [
            "curl {ADMIN_PREFIX}/certificate-signed/1/mark.json",
            "curl --form 'action=active' {ADMIN_PREFIX}/certificate-signed/1/mark.json",
        ],
    },
    "/certificate-signed/upload.json": {
        "endpoint": "/certificate-signed/upload.json",
        "section": "certificate-signed",
        "about": """Upload a certificate""",
        "POST": True,
        "GET": None,
        "GET-SELF-DOCUMENTING": True,
        "args": None,
        "examples": [
            "curl http://127.0.0.1:7201/.well-known/admin/certificate-signed/upload.json",
            "curl --form 'private_key_file_pem=@privkey1.pem' --form 'certificate_file=@cert1.pem' --form 'chain_file=@chain1.pem' {ADMIN_PREFIX}/certificate-signed/upload.json",
        ],
    },
    "/certificate-requests.json": {
        "endpoint": "/certificate-requests.json",
        "section": "certificate-request",
        "about": """list certificate-requests""",
        "POST": True,
        "GET": True,
        "args": None,
        "args": None,
        "example": "curl http://127.0.0.1:7201/.well-known/admin/certificate-requests.json",
    },
    "/certificate-requests/{PAGE}.json": {
        "endpoint": "/certificate-requests/{PAGE}.json",
        "section": "certificate-request",
        "about": """list certificate-requests, paginated""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl http://127.0.0.1:7201/.well-known/admin/certificate-requests/1.json",
    },
    "/certificate-request/{ID}.json": {
        "endpoint": "/certificate-request/{ID}.json",
        "section": "certificate-request",
        "about": """certificate request info""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl http://127.0.0.1:7201/.well-known/admin/certificate-request/1.json",
    },
    "/certificate-request/{ID}/csr.csr": {
        "endpoint": "/certificate-request/{ID}/csr.csr",
        "section": "certificate-request",
        "about": """certificate request as CSR file""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl http://127.0.0.1:7201/.well-known/admin/certificate-request/1/csr.csr",
    },
    "/certificate-request/{ID}/csr.pem": {
        "endpoint": "/certificate-request/{ID}/csr.pem",
        "section": "certificate-request",
        "about": """certificate request in pem format""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl http://127.0.0.1:7201/.well-known/admin/certificate-request/1/csr.pem",
    },
    "/certificate-request/{ID}/csr.pem.txt": {
        "endpoint": "/certificate-request/{ID}/csr.pem.txt",
        "section": "certificate-request",
        "about": """certificate request in pem.txt format""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl http://127.0.0.1:7201/.well-known/admin/certificate-request/1/csr.pem.txt",
    },
    "/domains/search.json": {
        "endpoint": "/domains/search.json",
        "section": "domain",
        "about": """search for a domain""",
        "POST": True,
        "GET": False,
        "GET-SELF-DOCUMENTING": True,
        "args": None,
        "examples": [
            "curl {ADMIN_PREFIX}/domains/search.json",
            "curl --form 'domain=example.com' {ADMIN_PREFIX}/domains/search.json",
        ],
    },
    "/domains.json": {
        "endpoint": "/domains.json",
        "section": "domain",
        "about": """list domains""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/domains.json",
    },
    "/domains/{PAGE}.json": {
        "endpoint": "/domains/{PAGE}.json",
        "section": "domain",
        "about": """list domains""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/domains/1.json",
    },
    "/domains/expiring.json": {
        "endpoint": "/domains/expiring.json",
        "section": "domain",
        "about": """list expiring domains""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/domains/expiring.json",
    },
    "/domains/expiring/{PAGE}.json": {
        "endpoint": "/domains/expiring/{PAGE}.json",
        "section": "domain",
        "about": """list expiring domains""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/domains/expiring/1.json",
    },
    "/domains/challenged.json": {
        "endpoint": "/domains/challenged.json",
        "section": "domain",
        "about": """list challenged domains""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/domains/challenged.json",
    },
    "/domains/challenged/{PAGE}.json": {
        "endpoint": "/domains/challenged/{PAGE}.json",
        "section": "domain",
        "about": """list challenged domains""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/domains/challenged/1.json",
    },
    "/domain/{DOMAIN|ID}.json": {
        "endpoint": "/domain/{DOMAIN|ID}.json",
        "section": "domain",
        "about": """core record as json""",
        "POST": True,
        "GET": None,
        "args": None,
        "examples": [
            "curl {ADMIN_PREFIX}/domain/1.json",
            "curl {ADMIN_PREFIX}/domain/example.com.json",
        ],
    },
    "/domain/{ID}/calendar.json": {
        "endpoint": "/domain/{ID}/calendar.json",
        "section": "domain",
        "about": """renewal calendar""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/domain/1/calendar.json",
    },
    "/domain/{DOMAIN|ID}/config.json": {
        "endpoint": "/domain/{DOMAIN|ID}/config.json",
        "section": "domain",
        "about": """certificate configuration info for a domain""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/domain/1/config.json",
    },
    "/domain/{ID}/nginx-cache-expire.json": {
        "endpoint": "/domain/{ID}/nginx-cache-expire.json",
        "section": "domain",
        "about": """send cache reset to Nginx for this domain""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/domain/1/nginx-cache-expire.json",
    },
    "/domain/{ID}/mark.json": {
        "endpoint": "/domain/{ID}/mark.json",
        "section": "domain",
        "about": """mark a domain""",
        "POST": True,
        "GET": None,
        "GET-SELF-DOCUMENTING": True,
        "args": None,
        "example": "curl --form 'action=active' {ADMIN_PREFIX}/domain/1/mark.json",
    },
    "/private-keys.json": {
        "endpoint": "/private-keys.json",
        "section": "private-key",
        "about": """list keys""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/private-keys.json",
    },
    "/private-keys/{PAGE}.json": {
        "endpoint": "/private-keys/{PAGE}.json",
        "section": "private-key",
        "about": """list keys, paginated""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/private-keys/1.json",
    },
    "/private-key/{ID}.json": {
        "endpoint": "/private-key/{ID}.json",
        "section": "private-key",
        "about": """Focus on the key""",
        "POST": True,
        "GET": False,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/private-key/1.json",
    },
    "/private-key/{ID}/parse.json": {
        "endpoint": "/private-key/{ID}/parse.json",
        "section": "private-key",
        "about": """Parse the key""",
        "POST": True,
        "GET": False,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/private-key/1/parse.json",
    },
    "/private-key/{ID}/key.key": {
        "endpoint": "/private-key/{ID}/key.key",
        "section": "private-key",
        "about": """download the key as a key (der)""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/private-key/1/key.key",
    },
    "/private-key/{ID}/key.pem": {
        "endpoint": "/private-key/{ID}/key.pem",
        "section": "private-key",
        "about": """download the key as a pem (pem)""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/private-key/1/key.pem",
    },
    "/private-key/{ID}/key.pem.txt": {
        "endpoint": "/private-key/{ID}/key.pem.txt",
        "section": "private-key",
        "about": """download the key as a pem (pem.txt)""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/private-key/1/key.pem.txt",
    },
    "/private-key/{ID}/mark.json": {
        "endpoint": "/private-key/{ID}/mark.json",
        "section": "private-key",
        "about": """mark the key""",
        "POST": True,
        "GET": False,
        "GET-SELF-DOCUMENTING": True,
        "args": None,
        "examples": [
            "curl {ADMIN_PREFIX}/private-key/1/mark.json",
            "curl --form 'action=active' {ADMIN_PREFIX}/private-key/1/mark.json",
        ],
    },
    "/private-key/{ID}/upload.json": {
        "endpoint": "/private-key/{ID}/upload.json",
        "section": "private-key",
        "about": """upload a key""",
        "POST": True,
        "GET": False,
        "GET-SELF-DOCUMENTING": True,
        "args": None,
        "examples": [
            "curl {ADMIN_PREFIX}/private-key/1/upload.json",
            "curl --form 'private_key_file_pem=@privkey1.pem' {ADMIN_PREFIX}/private-key/1/upload.json",
        ],
    },
    "/queue-domains.json": {
        "endpoint": "/queue-domains.json",
        "section": "queue-domain",
        "about": """list domains in queue (unprocessed)""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/queue-domains.json",
    },
    "/queue-domains/{PAGE}.json": {
        "endpoint": "/queue-domains/{PAGE}.json",
        "section": "queue-domain",
        "about": """list domains in queue (unprocessed), paginated""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/queue-domains/1.json",
    },
    "/queue-domains/all.json": {
        "endpoint": "/queue-domains/all.json",
        "section": "queue-domain",
        "about": """list domains in queue (all)""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/queue-domains/all.json",
    },
    "/queue-domains/all/{PAGE}.json": {
        "endpoint": "/queue-domains/all/{PAGE}.json",
        "section": "queue-domain",
        "about": """list domains in queue (all), paginated""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/queue-domains/all/1.json",
    },
    "/queue-domains/add.json": {
        "endpoint": "/queue-domains/add.json",
        "section": "queue-domain",
        "about": """queue domains""",
        "POST": True,
        "GET": None,
        "GET-SELF-DOCUMENTING": True,
        "args": None,
        "examples": [
            "curl {ADMIN_PREFIX}/queue-domains/add.json",
            'curl --form "domain_names=example.com,foo.example.com" {ADMIN}/queue-domains/add.json',
        ],
    },
    "/queue-domains/process.json": {
        "endpoint": "/queue-domains/process.json",
        "section": "queue-domain",
        "about": """engage queue""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/queue-domains/process.json",
    },
    "/queue-domain/{ID}.json": {
        "endpoint": "/queue-domain/{ID}.json",
        "section": "queue-domain",
        "about": """focus on record""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/queue-domain/1.json",
    },
    "/queue-domain/{ID}/mark.json": {
        "endpoint": "/queue-domain/{ID}/mark.json",
        "section": "queue-domain",
        "about": """mark the queue item""",
        "POST": True,
        "GET": None,
        "GET-SELF-DOCUMENTING": True,
        "args": None,
        "examples": [
            "curl {ADMIN_PREFIX}/queue-domain/1/mark.json",
            'curl --form "action=cancel" {ADMIN_PREFIX}/queue-domain/1/mark.json',
        ],
    },
    "/queue-certificates.json": {
        "endpoint": "/queue-certificates.json",
        "section": "queue-certificate",
        "about": """list renewals in queue (unprocessed)""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/queue-certificates.json",
    },
    "/queue-certificates/{PAGE}.json": {
        "endpoint": "/queue-certificates/{PAGE}.json",
        "section": "queue-certificate",
        "about": """list renewals in queue (unprocessed), paginated""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/queue-certificates/1.json",
    },
    "/queue-certificates/all.json": {
        "endpoint": "/queue-certificates/all.json",
        "section": "queue-certificate",
        "about": """list renewals in queue (all)""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/queue-certificates/all.json",
    },
    "/queue-certificates/all/{PAGE}.json": {
        "endpoint": "/queue-certificates/all/{PAGE}.json",
        "section": "queue-certificate",
        "about": """list renewals in queue (all), paginated""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/queue-certificates/all/1.json",
    },
    "/queue-certificates/active-failures.json": {
        "endpoint": "/queue-certificates/active-failures.json",
        "section": "queue-certificate",
        "about": """list renewals in queue (active-failures)""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/queue-certificates/active-failures.json",
    },
    "/queue-certificates/active-failures/{PAGE}.json": {
        "endpoint": "/queue-certificates/active-failures/{PAGE}.json",
        "section": "queue-certificate",
        "about": """list renewals in queue (active-failures), paginated""",
        "POST": True,
        "GET": True,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/queue-certificates/active-failures/1.json",
    },
    "/queue-certificate/{ID}.json": {
        "endpoint": "/queue-certificate/{ID}.json",
        "section": "queue-certificate",
        "about": """focus on record""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/queue-certificate/1.json",
    },
    "/queue-certificate/{ID}/mark.json": {
        "endpoint": "/queue-certificate/{ID}/mark.json",
        "section": "queue-certificate",
        "about": """mark the queue item""",
        "POST": True,
        "GET": None,
        "GET-SELF-DOCUMENTING": True,
        "args": None,
        "examples": [
            "curl {ADMIN_PREFIX}/queue-certificate/1/mark.json",
            'curl --form "action=cancel" {ADMIN_PREFIX}/queue-certificate/1/mark.json',
        ],
    },
    "/unique-fqdn-sets.json": {
        "endpoint": "/unique-fqdn-sets.json",
        "section": "unique-fqdn-set",
        "about": """list as json""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/unique-fqdn-sets.json",
    },
    "/unique-fqdn-sets/1.json": {
        "endpoint": "/unique-fqdn-sets/1.json",
        "section": "unique-fqdn-set",
        "about": """list as json, paginated""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/unique-fqdn-sets/1.json",
    },
    "/unique-fqdn-set/{ID}.json": {
        "endpoint": "/unique-fqdn-set/{ID}.json",
        "section": "unique-fqdn-set",
        "about": """info as json""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/unique-fqdn-set/1.json",
    },
    "/unique-fqdn-set/{ID}/calendar.json": {
        "endpoint": "/unique-fqdn-set/{ID}/calendar.json",
        "section": "unique-fqdn-set",
        "about": """renewal calendar""",
        "POST": True,
        "GET": None,
        "args": None,
        "example": "curl {ADMIN_PREFIX}/unique-fqdn-set/1/calendar.json",
    },
}
