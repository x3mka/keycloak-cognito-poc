from onelogin.saml2.auth import OneLogin_Saml2_Auth
from app.saml.saml_settings import get_saml_settings


def prepare_flask_request(request):
    return {
        'http_host': request.url.hostname,
        'script_name': request.scope.get("root_path", ""),
        'server_port': request.url.port or ('443' if request.url.scheme == 'https' else '80'),
        'get_data': request.query_params._dict,
        'post_data': {},
        'https': 'on' if request.url.scheme == 'https' else 'off',
    }

async def prepare_flask_post_request(request):
    form = await request.form()
    return {
        'http_host': request.url.hostname,
        'script_name': request.scope.get("root_path", ""),
        'server_port': request.url.port or ('443' if request.url.scheme == 'https' else '80'),
        'get_data': request.query_params._dict,
        "post_data": form,  # ✅ сюда попадает SAMLResponse!
        "https": "on" if request.url.scheme == "https" else "off",
    }


def init_saml_auth(req):
    settings = get_saml_settings()
    return OneLogin_Saml2_Auth(req, old_settings=settings)
