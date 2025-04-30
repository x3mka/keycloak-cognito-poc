from onelogin.saml2.settings import OneLogin_Saml2_Settings
from dotenv import load_dotenv
import os

load_dotenv()

def get_saml_settings():
    saml_path = os.path.join(os.path.dirname(__file__), "../../sp_metadata")
    settings = {
        "strict": True,
        "debug": True,
        "sp": {
            "entityId": os.getenv("SAML_SP_ENTITY_ID"),
            "assertionConsumerService": {
                "url": os.getenv("SAML_SP_ASSERTION_CONSUMER_SERVICE"),
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            "x509cert": open(f"{saml_path}/cert.pem").read(),
            "privateKey": open(f"{saml_path}/key.pem").read(),
        },
        "idp": {
            "entityId": os.getenv("SAML_IDP_ENTITY_ID"),
            "singleSignOnService": {
                "url": os.getenv("SAML_IDP_SSO_URL"),
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            "x509cert": os.getenv("SAML_IDP_X509_CERT").replace('\\n', '\n'),
        },
        "security": {
            "allowRepeatAttributeName": True
        }
    }
    return OneLogin_Saml2_Settings(settings, custom_base_path=saml_path)
