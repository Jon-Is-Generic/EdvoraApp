# EdvoraApp

Application for Edvora. To quote their requirement:
> We would like to see your work before we proceed further with the screening process. As our filtering test, we would like you to create an authenticated feed system using FastAPI and Socket.IO. It needs to have login/logout functionality with session management, such as terminating other active sessions of the same user from one session. The feed should have the username and message, and should be broadcasted to all authenticated users connected via websockets. You may create a frontend to showcase the submission, but it is not necessary. Extra points if you can make it keeping scalability and efficiency in mind.

# Client side

An example client has been provided within the example folder.

## API

For the basics of the API, use http://localhost:5000/docs - assuming you're running this locally, as it's configured to. It explains the basics of register and login and such. Note that logout is relatively useless, since this uses Bearer tokens - simply throw away the bearer token. Logging in provides a bearer token for the websocket, which I'll explain below

## Socket.IO

To use the Socket.IO stuff, use the bearer tokens as authentication (see examples for details), and connect. The two types of events it processes are `message`, and `logout_all` - the former sends a message (your data) to all other connections (your own messages won't be emitted back to you), and the latter disconnects not only the connection that asks for it, but also all connections for the same user - corresponding with the "terminating other active sessions of the same user from one session" requirement.

## Expandability

I made some notes in the code where scalability and efficient could be improved, but didn't have the chance to do so. If necessary, I can try to provide such alterations.

# Server side

To deploy the server, simply run `main.py` wherever you would like. If this is meant to be a "real system" change your SECRET in my_users.py to something else.

## Additional Notes

If you're wondering about the file names, I found it simply made tracking things less confusing.
