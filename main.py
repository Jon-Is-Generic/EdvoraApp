import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.my_app:sio_app", host="0.0.0.0", port=5000, log_level="info")
