from flask import Flask
from flask_cors import CORS
from database import initialize_database
from qualityRoutes import qualityRoutes
from diseaseRoutes import diseaseRoutes
from userRoutes import configure_jwt_secret, userRoutes

app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes
# CORS(app, origins='http://localhost:3000')
CORS(app, origins='http://localhost:3000', supports_credentials=True)
app.config['MONGO_URI'] = 'mongodb+srv://jg-cabauatan:EIT7I1S7SCBaCJZO@itp-backend.a0fhlie.mongodb.net/db_kalamansi?retryWrites=true&w=majority'
app.config['MONGO_DB'] = 'db_kalamansi'
app.config['JWT_SECRET'] = 'hOBIEr9b5guVvBE5IGBeVqwrBAW7NuUS' 

# Initialize database connection
db = initialize_database(app)


# Register quality and disease routes blueprints
app.register_blueprint(qualityRoutes)
app.register_blueprint(diseaseRoutes)
app.register_blueprint(userRoutes)

# Pass JWT secret key to userRoutes.py
configure_jwt_secret(app.config['JWT_SECRET'])



if __name__ == '__main__':
    app.run(debug=True)