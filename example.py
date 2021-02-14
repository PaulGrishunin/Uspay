
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route


async def app(scope, receive, send):
    assert scope['type'] == 'http'

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
    return JSONResponse({'register': 'name'})


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
