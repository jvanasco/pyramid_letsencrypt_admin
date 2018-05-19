from invoke import Collection, run, task

import os
import os.path
import subprocess
import json
import pprint

# ==============================================================================

_le_archive_filename_templates = {'certificate': 'cert%d.pem',
                                  'chain': 'chain%d.pem',
                                  'fullchain': 'fullchain%d.pem',
                                  'private_key': 'privkey%d.pem',
                                  }
_le_live_filenames = {'certificate': 'cert.pem',
                      'chain': 'chain.pem',
                      'fullchain': 'fullchain.pem',
                      'private_key': 'privkey.pem',
                      }
_le_account_filenames = ['private_key.json',
                         'meta.json',
                         'regr.json',
                         ]


def upload_fileset(server_url_root, fset):
    """actually uploads a fileset"""
    if server_url_root[-1] == '/':
        server_url_root = server_url_root[:-1]
    url = '%s/certificate/upload.json' % server_url_root

    proc = subprocess.Popen(['curl',
                             "--form", "private_key_file=@%s" % fset['private_key'],
                             "--form", "certificate_file=@%s" % fset['certificate'],
                             "--form", "chain_file=@%s" % fset['chain'],
                             url
                             ],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    json_response, err = proc.communicate()
    try:
        if not json_response:
            raise ValueError("error")
        json_response = json.loads(json_response)
        if ('result' not in json_response) or (json_response['result'] != 'success'):
            pprint.pprint(json_response)
            raise ValueError("error!")
        else:
            print("success | %s" % json_response)
    except Exception as exc:
        raise


def upload_account(server_url_root, fset):
    """actually uploads an account fileset"""
    if server_url_root[-1] == '/':
        server_url_root = server_url_root[:-1]
    url = '%s/account-key/upload.json' % server_url_root

    proc = subprocess.Popen(['curl',
                             "--form", "account_key_file_le_pkey=@%s" % fset['private_key.json'],
                             "--form", "account_key_file_le_meta=@%s" % fset['meta.json'],
                             "--form", "account_key_file_le_reg=@%s" % fset['regr.json'],
                             url
                             ],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    json_response, err = proc.communicate()
    try:
        if not json_response:
            raise ValueError("error")
        json_response = json.loads(json_response)
        if ('result' not in json_response) or (json_response['result'] != 'success'):
            pprint.pprint(json_response)
            raise ValueError("error!")
        else:
            print("success | %s" % json_response)
    except Exception as exc:
        raise


@task(help={'archive_path': "Path to letsencrypt archive files.",
            'server_url_root': "URL of server to post to, do not include `.well-known`",
            })
def import_letsencrypt_certs_archive(c, archive_path, server_url_root):
    """imports the entire letescrypt archive on `archive_path`
    HEY THIS PROBABLY HAPPENS ON UNENCRYPTED TRAFFIC

    usage:
        invoke import-letsencrypt-certs-archive --archive-path="/path/to/archive" --server-url-root="http://0.0.0.0:7201/.well-known/admin"
        invoke import-letsencrypt-certs-archive --archive-path="/etc/letsencrypt/archive" --server-url-root="http://0.0.0.0:7201/.well-known/admin"
    """
    if not archive_path:
        raise ValueError("missing `archive-path`")
        
    if server_url_root[:4] != 'http':
        raise ValueError("`server_url_root` does not look like a url")

    if not os.path.isdir(archive_path):
        raise ValueError("`%s` is not a directory" % archive_path)

    # grab all the directories
    dirs = [i for i in os.listdir(archive_path) if i[0] != '.']

    # empty queue
    filesets = []

    for d in dirs:
        dpath = os.path.join(archive_path, d)
        if not os.path.isdir(dpath):
            raise ValueError("`%s` is not a directory" % dpath)
        dfiles = [f for f in os.listdir(dpath) if f[0] != '.']
        # ensure we have the right files in here...
        if not dfiles:
            # no files, GREAT!
            continue
        # we best only have sets of 4 files...
        if len(dfiles) % 4:
            raise ValueError("`%s` does not look to be a letsencrypt directory" % dpath)
        total_sets = len(dfiles) / 4
        for i in range(1, total_sets + 1):
            fset = {}
            for (ftype, ftemplate) in _le_archive_filename_templates.items():
                fpath = os.path.join(dpath, ftemplate % i)
                if not os.path.exists(fpath):
                    raise ValueError("`%s` does not look to be a letsencrypt directory; expected %s" % (dpath, fpath))
                fset[ftype] = fpath
            filesets.append(fset)

    if not filesets:
        raise ValueError("No files!")

    for fset in filesets:
        upload_fileset(server_url_root, fset)
    return


@task(help={'domain_certs_path': "Path to letsencrypt archive files for a domain.",
            'certificate_version': "digit. the certificate version you want.",
            'server_url_root': "URL of server to post to, do not include `.well-known`",
            })
def import_letsencrypt_cert_version(c, domain_certs_path, certificate_version, server_url_root):
    """imports the archive path for a version

    eg, if a folder has a family of certs numbered like this:
        /domain-certs/fullchain1.pem
        /domain-certs/fullchain2.pem
        /domain-certs/fullchain3.pem
    
    you can import a specific version, for example "3", with this command

    usage:
        invoke import_letsencrypt_cert_version --domain-certs-path="/path/to/ssl/archive/example.com" --certificate-version=3 --server-url-root="http://0.0.0.0:7201/.well-known/admin"
    """
    if not domain_certs_path:
        raise ValueError("missing `domain-certs-path`")

    if not certificate_version.isdigit():
        raise ValueError("missing `certificate-version must be a digit`")
    certificate_version = int(certificate_version)

    if server_url_root[:4] != 'http':
        raise ValueError("`server_url_root` does not look like a url")

    if not os.path.isdir(domain_certs_path):
        raise ValueError("`%s` is not a directory" % domain_certs_path)
        
    _missing_files = []
    _fileset = {}
    for (ftype, ftemplate) in _le_archive_filename_templates.items():
        flocal = ftemplate % certificate_version
        fpath = os.path.join(domain_certs_path, flocal)
        if not os.path.exists(fpath):
            _missing_files.append(flocal)
        else:
            _fileset[ftype] = fpath
    if _missing_files:
        raise ValueError("Missing files in `%s`: %s" % (domain_certs_path, ','.join(_missing_files)))

    upload_fileset(server_url_root, _fileset)
    return


@task(help={'cert_path': "Path to cert folder.",
            'server_url_root': "URL of server to post to, do not include `.well-known`",
            })
def import_letsencrypt_cert_plain(c, cert_path, server_url_root):
    """imports the certificate for a folder, given an unversioned content structure:

        /domain-cert/certificate.pem
        /domain-cert/chain.pem
        /domain-cert/fullchain.pem
        /domain-cert/private_key.pem
    
    usage:
        invoke import_letsencrypt_cert_plain --cert-path="/path/to/ssl/live/example.com" --server-url-root="http://0.0.0.0:7201/.well-known/admin"
    """
    if not cert_path:
        raise ValueError("missing `cert-path`")

    if server_url_root[:4] != 'http':
        raise ValueError("`server_url_root` does not look like a url")

    if not os.path.isdir(cert_path):
        raise ValueError("`%s` is not a directory" % cert_path)
        
    _missing_files = []
    _fileset = {}
    for (ftype, fname) in _le_live_filenames.items():
        fpath = os.path.join(cert_path, fname)
        if not os.path.exists(fpath):
            _missing_files.append(fname)
        else:
            _fileset[ftype] = fpath
    if _missing_files:
        raise ValueError("Missing files in `%s`: %s" % (cert_path, ','.join(_missing_files)))

    upload_fileset(server_url_root, _fileset)
    return


@task(help={'live_path': "Path to letsencrypt live files. should be `/etc/letsencrypt/live`",
            'server_url_root': "URL of server to post to, do not include `.well-known`",
            })
def import_letsencrypt_certs_live(c, live_path, server_url_root):
    """imports the letsencrypt live archive  in /etc/letsencrypt/live

    usage:
        invoke import_letsencrypt_certs_live --live-path="/etc/letsencrypt/live" --server-url-root="http://0.0.0.0:7201/.well-known/admin"
    """
    if not live_path:
        raise ValueError("missing `live-path`")

    if server_url_root[:4] != 'http':
        raise ValueError("`server_url_root` does not look like a url")

    if not os.path.isdir(live_path):
        raise ValueError("`%s` is not a directory" % live_path)
        
    # grab all the directories
    dirs = [i for i in os.listdir(live_path) if i[0] != '.']

    # empty queue
    filesets = []

    for d in dirs:
        dpath = os.path.join(live_path, d)
        if not os.path.isdir(dpath):
            raise ValueError("`%s` is not a directory" % dpath)
        dfiles = [f for f in os.listdir(dpath) if f[0] != '.']
        # ensure we have the right files in here...
        if len(dfiles) != 4:
            raise ValueError("`%s` does not look to be a letsencrypt directory" % dpath)

        fset = {}
        for (ftype, fname) in _le_live_filenames.items():
            fpath = os.path.join(dpath, fname)
            if not os.path.exists(fpath):
                raise ValueError("`%s` does not look to be a letsencrypt directory; expected %s" % (dpath, fpath))
            fset[ftype] = fpath
        filesets.append(fset)

    if not filesets:
        raise ValueError("No files!")

    for fset in filesets:
        upload_fileset(server_url_root, fset)
    return


# ==============================================================================


def _accountPath_to_fileSet(account_path):
    dfiles = [f for f in os.listdir(account_path) if f[0] != '.']
    # ensure we have the right files in here...
    if len(dfiles) != 3:
        raise ValueError("`%s` does not look to be a letsencrypt account directory" % account_path)
    fset = {}
    for fname in _le_account_filenames:
        fpath = os.path.join(account_path, fname)
        if not os.path.exists(fpath):
            raise ValueError("`%s` does not look to be a letsencrypt account directory; expected %s" % (account_path, fname))
        fset[fname] = fpath
    return fset


@task(help={'account_path': "Path to letsencrypt account files. should be `/etc/letsencrypt/accounts/{SERVER}/directory/{ACCOUNT}`",
            'server_url_root': "URL of server to post to, do not include `.well-known`",
            })
def import_letsencrypt_account(c, account_path, server_url_root):
    """imports a specific letsencrypt account

    usage:
        invoke import_letsencrypt_account --account-path="/etc/letsencrypt/accounts/{SERVER}/directory/{ACCOUNT}" --server-url-root="http://0.0.0.0:7201/.well-known/admin"
    """
    if not account_path:
        raise ValueError("missing `account-path`")

    if server_url_root[:4] != 'http':
        raise ValueError("`server_url_root` does not look like a url")

    if not os.path.isdir(account_path):
        raise ValueError("`%s` is not a directory" % account_path)
    
    fset = _accountPath_to_fileSet(account_path)
    upload_account(server_url_root, fset)
    return


@task(help={'server_accounts_path': "Path to letsencrypt server account files. should be `/etc/letsencrypt/accounts/{SERVER}`",
            'server_url_root': "URL of server to post to, do not include `.well-known`",
            })
def import_letsencrypt_accounts_server(c, accounts_path_server, server_url_root):
    """imports all accounts for a given letsencrypt server

    usage:
        invoke import_letsencrypt_accounts_server --accounts-path-server="/etc/letsencrypt/accounts/{SERVER}" --server-url-root="http://0.0.0.0:7201/.well-known/admin"
    """
    if not accounts_path_server:
        raise ValueError("missing `accounts-path-server`")

    if server_url_root[:4] != 'http':
        raise ValueError("`server_url_root` does not look like a url")

    if not os.path.isdir(accounts_path_server):
        raise ValueError("`%s` is not a directory" % accounts_path_server)
        
    dfiles = [f for f in os.listdir(accounts_path_server) if f[0] != '.']
    # ensure we have the right files in here...
    if (len(dfiles) != 1) or ('directory' not in dfiles):
        raise ValueError("`%s` does not look to be a letsencrypt server account directory" % accounts_path_server)

    dpath_directory = os.path.join(accounts_path_server, 'directory')
    account_directories = [f for f in os.listdir(dpath_directory) if f[0] != '.']
    if (not account_directories):
        raise ValueError("`%s` does not have any accounts" % dpath_directory)

    filesets = []
    for account_hash in account_directories:
        account_path = os.path.join(dpath_directory, account_hash)
        account_fset = _accountPath_to_fileSet(account_path)
        filesets.append(account_fset)

    if not filesets:
        raise ValueError("no filesets detected")
    for fset in filesets:
        upload_account(server_url_root, fset)
    return


@task(help={'accounts_all_path': "Path to letsencrypt server account files. should be `/etc/letsencrypt/accounts`",
            'server_url_root': "URL of server to post to, do not include `.well-known`",
            })
def import_letsencrypt_accounts_all(c, accounts_all_path, server_url_root):
    """imports all accounts for a letsencrypt install

    usage:
        invoke import_letsencrypt_accounts_all --accounts-all-path="/etc/letsencrypt/accounts" --server-url-root="http://0.0.0.0:7201/.well-known/admin"
    """
    if not accounts_all_path:
        raise ValueError("missing `accounts-all-path`")

    if server_url_root[:4] != 'http':
        raise ValueError("`server_url_root` does not look like a url")

    if not os.path.isdir(accounts_all_path):
        raise ValueError("`%s` is not a directory" % accounts_all_path)

    serverNames = [f for f in os.listdir(accounts_all_path) if f[0] != '.']
    # ensure we have the right files in here...
    if (not len(serverNames)) or (not all([True if d.startswith('acme-') else False
                                           for d in serverNames
                                           ])):
        raise ValueError("`%s` does not look to be a letsencrypt accounts directory" % accounts_all_path)
        
    filesets = []

    for sname in serverNames:
        accounts_path_server =  os.path.join(accounts_all_path, sname)
        dpath_directory = os.path.join(accounts_path_server, 'directory')
        account_directories = [f for f in os.listdir(dpath_directory) if f[0] != '.']
        if (not account_directories):
            raise ValueError("`%s` does not have any accounts" % dpath_directory)

        for account_hash in account_directories:
            account_path = os.path.join(dpath_directory, account_hash)
            account_fset = _accountPath_to_fileSet(account_path)
            filesets.append(account_fset)

    if not filesets:
        raise ValueError("no filesets detected")
    
    for fset in filesets:
        upload_account(server_url_root, fset)
    return


# ==============================================================================


namespace = Collection(import_letsencrypt_certs_archive,
                       import_letsencrypt_certs_live,
                       import_letsencrypt_cert_version,
                       import_letsencrypt_cert_plain,

                       import_letsencrypt_account,
                       import_letsencrypt_accounts_server,
                       import_letsencrypt_accounts_all,
                       )
