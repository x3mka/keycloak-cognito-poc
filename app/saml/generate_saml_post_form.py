import base64
from app.saml.utils import init_saml_auth, prepare_flask_request


def generate_saml_post_form(request):
    saml_auth = init_saml_auth(prepare_flask_request(request))
    saml_auth.login()  # для генерации внутреннего запроса
    saml_request_xml = saml_auth.get_last_request_xml()
    saml_request_encoded = base64.b64encode(saml_request_xml.encode()).decode()

    sso_url = saml_auth.get_sso_url()

    return f"""
    <html>
    <body onload="document.forms[0].submit()">
        <p>Перенаправление к поставщику идентификации...</p>
        <form method="post" action="{sso_url}">
            <input type="hidden" name="SAMLRequest" value="{saml_request_encoded}" />
            <input type="submit" value="Продолжить" />
        </form>
    </body>
    </html>
    """