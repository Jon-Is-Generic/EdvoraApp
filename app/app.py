from typing import Union, Any, AsyncGenerator

from fastapi import Depends, FastAPI
from fastapi_users.authentication.strategy import BaseAccessToken
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase

from app.db import database, get_access_token_db, session, AccessTokenTable, UserTable
from app.models import UserDB, User
from app.users import auth_backend, current_active_user, fastapi_users
import socketio

app = FastAPI()
sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi') # We don't care how they send it
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

def get_db (access_token_db : Depends(get_access_token_db)):
    pass

@sio.event
def connect(sid, environ, auth):
    try:
        token = auth['token']
    except TypeError:
        token = None
    if token is None:
        raise ConnectionRefusedError('authentication failed')
    print("connect ", sid, "auth: ", auth)
    z = session.query(AccessTokenTable).filter_by(token=token).first()
    if z is None:
        raise ConnectionRefusedError('authentication failed')
    user_id = z.user_id
    print("Found entry", user_id)
    # TODO - store user_id somewhere.
    username = session.query(UserTable).filter_by(id=user_id).first()
    if username is None:
        raise IndexError('invalid user')
    username = username.email
    print("Thanks for logging in", username)

@sio.event
async def message(sid, data):
    print("message received", data)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)
