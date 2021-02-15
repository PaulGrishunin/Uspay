from starlette.responses import PlainTextResponse
import databases
import sqlalchemy
from starlette.applications import Starlette
from starlette.config import Config
from starlette.responses import JSONResponse
from starlette.routing import Route

# Configuration from environment variables or '.env' file.
config = Config('.env')
DATABASE_URL = config('DATABASE_URL')

# Database table definitions.
metadata = sqlalchemy.MetaData()

notes = sqlalchemy.Table(
    "notes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("login", sqlalchemy.String),
    sqlalchemy.Column("password", sqlalchemy.String),
)

database = databases.Database(DATABASE_URL)

# Main application code.
async def list_users(request):
    query = users.select()
    results = await database.fetch_all(query)
    content = [
        {
            "login": result["login"],
            "password": result["password"]
        }
        for result in results
    ]
    return JSONResponse(content)

async def add_user(request):
    data = await request.json()
    query = users.insert().values(
       login=data["login"],
       password=data["password"]
    )
    await database.execute(query)
    return JSONResponse({
        "login": data["login"],
        "password": data["password"]
    })

routes = [
    Route("/", endpoint=list_users, methods=["GET"]),
    Route("/register", endpoint=add_user, methods=["POST"]),
]

app = Starlette(
    routes=routes,
    on_startup=[database.connect],
    on_shutdown=[database.disconnect]
)


async def app(scope, receive, send):
    assert scope['type'] == 'http'
    response = PlainTextResponse("Hello, world!")
    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            [b'content-type', b'text/plain'],
        ],
    })
    await send({
        'type': 'http.response.body',
        'body': b'Hello, world!',
    })


async def homepage(request):
    return JSONResponse({'hello': 'world'})

async def register(request):
    return JSONResponse({'logim': 'password'})


app = Starlette(debug=True, routes=[
    Route('/', homepage),
    Route('/register', register),
    
])

@app.route('/create-user', methods=['POST'])
def create_user():
    id = request.form.get('id', '0001')
    name = request.form.get('name', 'Anonymous')
    # код для аутентификации, валидации, обновления базы данных
    data = {'id': id, 'name': name}
    result = {'status_code': '0', 'status_message' : 'Success', 'data': data}
    return jsonify(result)


if __name__ == "__main__":
    uvicorn.run("example:app", host="127.0.0.1", port=5000, log_level="info")
