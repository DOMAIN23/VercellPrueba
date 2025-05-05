from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'app/uploads'

    from app.route import init_routes
    init_routes(app)

    return app
