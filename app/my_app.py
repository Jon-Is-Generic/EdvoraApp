import socketio
from fastapi import Depends, FastAPI

from app.my_db import database, session, AccessTokenTable, UserTable
from app.my_models import UserDB
from app.my_users import auth_backend, current_active_user, fastapi_users

app = FastAPI()
sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')  # We don't care how they send it
sio_app = socketio.ASGIApp(sio, app)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/db", tags=["auth"]
)
app.include_router(fastapi_users.get_register_router(), prefix="/auth", tags=["auth"])
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(fastapi_users.get_users_router(), prefix="/users", tags=["users"])


@app.get("/authenticated-route")
async def authenticated_route(user: UserDB = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}

@app.on_event("startup")
async def startup():
    await database.connect()
    session.begin()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    session.close()


@sio.event
async def connect(sid, environ, auth):
    try:
        token = auth['token']
    except TypeError:
        token = None
    if token is None:
        raise ConnectionRefusedError('authentication failed')
    z = session.query(AccessTokenTable).filter_by(token=token).first()
    if z is None:
        raise ConnectionRefusedError('authentication failed')
    user_id = z.user_id
    username = session.query(UserTable).filter_by(id=user_id).first()
    if username is None:
        raise IndexError('invalid user')
    username = username.email
    await sio.save_session(sid, {'username' : username, 'user_id' : user_id})
    sio.enter_room(sid, 'chat')
    print("Logged in:", username)

@sio.event
async def message(sid, data):
    session = await sio.get_session(sid)
    msg = f"{session['username']}: {data}"
    print(msg)
    await sio.emit('message', data=msg, skip_sid=sid, room='chat')
    # await sio.emit('message', data=msg, room='chat') # Swap the comments to make the sender receive a copy.

@sio.event
async def logout_all(sid, data):
    session = await sio.get_session(sid)
    user_id = session['user_id']
    await log_out_with_id(user_id)

@sio.event
async def disconnect(sid):
    print('disconnect ', sid)


async def log_out_with_id(user_id : str):
    for p in sio.manager.get_participants('/', 'chat'): # Understandably, this could be improved by keeping a dictionary tracking the sessions for each user. This was faster to write... if you really want that code, hire me and I'll do it.
        participant = p[0]
        try:
            session = await sio.get_session(participant)
            if session['user_id'] == user_id:
                await sio.emit('message', data="Logging out all sessions", to=participant)
                await sio.disconnect(participant)
        except KeyError:
            print("KEY ERROR")
