from os import environ

CREDENTIALS = {
    "type": environ.get('TYPE'),
    "project_id": environ.get('PROJECT_ID'),
    "private_key_id": environ.get('PRIVATE_KEY_ID'),
    "private_key": environ.get('PRIVATE_KEY'),
    "client_email": environ.get('CLIENT_EMAIL'),
    "client_id": environ.get('CLIENT_ID'),
    "auth_uri": environ.get('AUTH_URI'),
    "token_uri": environ.get('TOKEN_URI'),
    "auth_provider_x509_cert_url": environ.get('AUTH_PROVIDER_X509_CERT_URL'),
    "client_x509_cert_url": environ.get('CLIENT_X509_CERT_URL')
}

CSV_PATH = "./data"