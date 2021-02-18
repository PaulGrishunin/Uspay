import databases
import sqlalchemy

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route, Mount
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.config import Config
from starlette.responses import JSONResponse

from starlette.authentication import (
    AuthenticationBackend, AuthenticationError, SimpleUser, UnauthenticatedUser,
    AuthCredentials)
from starlette.authentication import requires
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
import base64
import binascii

templates = Jinja2Templates(directory='templates')

# Configuration from environment variables or '.env' file.
config = Config('.env')
DATABASE_URL = config('DATABASE_URL')
# Database table definitions.
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String),
    sqlalchemy.Column("password", sqlalchemy.String),
)
database = databases.Database(DATABASE_URL)


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        if "Authorization" not in request.headers:
            return

        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != 'basic':
                return
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
            raise AuthenticationError('Invalid basic auth credentials')

        username, _, password = decoded.partition(":")
        # TODO: You'd want to verify the username and password here.
        return AuthCredentials(["authenticated"]), SimpleUser(username)


async def user_register(request):
    #return PlainTextResponse("Registration")
    data = await request.json()
    query = users.insert().values(
        username=data["username"],
        password=data["password"]
    )
    """ Добавить проверку на существование "username" в базе, True-"User уже есть в базе"-переход к авторизации, False - запись и popup-сообщение "Зарегистрирован" """
    await database.execute(query)
    return JSONResponse({
        "username": data["username"],
        "password": data["password"]
    })
    

async def auth(request):
    return templates.TemplateResponse('index.html', {'request': request})
    #return PlainTextResponse("Authorization")

@requires('authenticated', redirect='auth')
async def dashboard(request):
    #async def get(self, request):
        #username = request.path_params['username']
        #return PlainTextResponse(f"Привет, {username}")
    #return JSONResponse({'hello': 'world'})
    if request.user.is_authenticated:
        return PlainTextResponse('Привет, ' + request.user.display_name)
    return PlainTextResponse('Hello, you')


async def logout(request):
    return PlainTextResponse("logout")


routes = [
    Route("/", endpoint=auth, methods=["GET", "POST"]),
    Route("/register", endpoint=user_register, methods=["POST"]),
    Route("/dashboard", endpoint=dashboard),
    Route("/logout", endpoint=logout, methods=["GET", "POST"]),
    Mount('/static', app=StaticFiles(directory='static', packages=['bootstrap4']), name="static"),
  
]

middleware = [
    Middleware(AuthenticationMiddleware, backend=BasicAuthBackend())
]

app = Starlette(debug=True, routes=routes, middleware=middleware)


#@app.route('/create-user', methods=['POST'])
#def create_user():
    #id = request.form.get('id', '0001')
    #name = request.form.get('name', 'Anonymous')
    #код для аутентификации, валидации, обновления базы данных
    #data = {'id': id, 'name': name}
    #result = {'status_code': '0', 'status_message' : 'Success', 'data': data}
    #return jsonify(result)
    
