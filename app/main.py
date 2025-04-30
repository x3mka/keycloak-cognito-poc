from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.saml.generate_saml_post_form import generate_saml_post_form
from app.saml.utils import init_saml_auth, prepare_flask_request, prepare_flask_post_request
from app.saml.saml_settings import get_saml_settings

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="super-secret-key")

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if "samlUserdata" in request.session:
        saml_session = {
            "name_id": request.session.get("nameid"),
            "attributes": request.session.get("samlUserdata", {})
        }
    else:
        saml_session = None

    return templates.TemplateResponse("home.html", {
        "request": request,
        "saml_session": saml_session,
    })

@app.get("/login")
async def login(request: Request):
    html = generate_saml_post_form(request)
    return HTMLResponse(content=html)

@app.get("/logout")
def logout(request: Request):
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)

    name_id = request.session.get("nameid")
    session_index = request.session.get("session_index")

    # Очищаем локальную сессию
    request.session.clear()

    # Перенаправляем на IdP logout
    return RedirectResponse(
        url=auth.logout(name_id=name_id, session_index=session_index)
    )

@app.api_route("/saml/acs", methods=["POST"])
async def acs(request: Request):
    req_data = await prepare_flask_post_request(request)
    saml_auth = init_saml_auth(req_data)

    saml_auth.process_response()
    errors = saml_auth.get_errors()

    # attrs = saml_auth.get_attributes()
    # print("Attrs:", attrs)

    debug_info = {
        "errors": errors,
        "last_error_reason": saml_auth.get_last_error_reason(),
        "last_response_xml": saml_auth.get_last_response_xml(),
        "name_id": saml_auth.get_nameid(),
        "session_index": saml_auth.get_session_index(),
        "attributes": saml_auth.get_attributes(),
    }

    if errors:
        from pprint import pformat
        return HTMLResponse(f"<pre>{pformat(debug_info)}</pre>", status_code=400)

    request.session["samlUserdata"] = debug_info["attributes"]
    request.session["nameid"] = debug_info["name_id"]
    request.session["session_index"] = debug_info["session_index"]
    return RedirectResponse("/", status_code=303)

@app.post("/saml/sls")
@app.get("/saml/sls")
def saml_logout_callback(request: Request):
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    auth.process_slo()
    return RedirectResponse(url="/")

@app.get("/saml/metadata")
async def metadata():
    settings = get_saml_settings()
    return Response(settings.get_sp_metadata(), media_type="text/xml")