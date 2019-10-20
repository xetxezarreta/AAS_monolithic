from application import create_app

app = create_app()
app.app_context().push()

if __name__ == "__main__":
    app.run(host='192.168.17.13', port=16000)

