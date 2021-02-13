from starlette.responses import PlainTextResponse

async def app(scope, receive, send):
    assert scope["type"] == "http"
    response = PlainTextResponse("Hello, world!!s!")
    await response(scope, receive, send) 
