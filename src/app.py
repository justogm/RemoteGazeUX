"""
Module docstring TODO: completar
"""

import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flasgger import Swagger
from db import DatabaseConfig, DatabaseManager, db, Subject, Measurement, User
from api.routes import api_bp
from state import ConfigManager
from repositories import (
    SubjectRepository,
    MeasurementRepository,
    StudyRepository,
    UserRepository,
)
from datetime import datetime


basedir = os.path.abspath(os.path.dirname(__file__))

config_manager = ConfigManager()
config_manager.load_config()

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# Secret key for sessions (change this to a random secret in production!)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

db_config = DatabaseConfig(basedir)
db_config.configure_app(app)

db_manager = DatabaseManager(app)

subject_repository = SubjectRepository()
measurement_repository = MeasurementRepository()
study_repository = StudyRepository()
user_repository = UserRepository()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Por favor inicia sesión para acceder a esta página."


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return user_repository.get_by_id(int(user_id))


app.register_blueprint(api_bp)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "User Gaze Track API",
        "description": "API for user gaze tracking and data management",
        "version": "1.0.0",
        "contact": {
            "name": "User Gaze Track Team",
        },
    },
    "host": "localhost:5001",
    "basePath": "/",
    "schemes": ["https", "http"],
    "securityDefinitions": {},
    "tags": [
        {"name": "web", "description": "Web interface routes"},
        {"name": "api", "description": "REST API endpoints"},
    ],
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login page for authentication.
    ---
    tags:
      - web
    parameters:
      - name: username
        in: formData
        type: string
        required: true
        description: Username for login.
      - name: password
        in: formData
        type: string
        required: true
        description: Password for login.
    responses:
      200:
        description: Login page or redirect to home on success.
      401:
        description: Invalid credentials.
    """
    # Redirect to home if already logged in
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = user_repository.get_user_by_username(username)

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page if next_page else url_for("index"))
        else:
            return render_template("login.html", error="Usuario o contraseña incorrectos")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """
    Logout the current user.
    ---
    tags:
      - web
    responses:
      302:
        description: Redirect to login page.
    """
    logout_user()
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main page that allows registration of a new subject for gaze measurement.
    ---
    parameters:
      - name: nombre
        in: formData
        type: string
        required: true
        description: Subject's name.
      - name: apellido
        in: formData
        type: string
        required: true
        description: Subject's surname.
      - name: edad
        in: formData
        type: integer
        required: true
        description: Subject's age.
    responses:
      200:
        description: Home page or redirect to tracking page.
    """
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        edad = request.form["edad"]

        # Get the active study ID
        active_study_id = app.config.get("ACTIVE_STUDY_ID")

        subject = subject_repository.create_subject(
            name=nombre, surname=apellido, age=edad, study_id=active_study_id
        )
        subject_repository.commit()

        return redirect(url_for("embed", id=subject.id))
    return render_template("index.html")


@app.route("/gaze-tracking")
def embed():
    """
    Shows the eye tracking page for the user with the ID passed as parameter.
    ---
    parameters:
      - name: id
        in: query
        type: integer
        required: true
        description: Subject ID for eye tracking.
    responses:
      200:
        description: Eye tracking page.
    """
    return render_template("embed.html", id=request.args.get("id"))


@app.route("/fin-medicion")
def fin_medicion():
    """
    Shows the measurement completion page.
    ---
    responses:
        200:
            description: Measurement completion page.
    """
    return render_template("fin.html")


@app.route("/estudios")
@login_required
def estudios():
    """
    Shows the list of all studies in the database.
    ---
    responses:
        200:
            description: Page with the list of all studies.
    """
    studies = study_repository.get_all_studies()
    return render_template("estudios.html", studies=studies)


@app.route("/sujetos")
@login_required
def sujetos():
    """
    Shows the list of registered subjects in the database.
    ---
    responses:
        200:
            description: Page with the list of registered subjects.
    """
    # Get all studies with their subjects
    studies = study_repository.get_all_studies()

    # Group subjects by study
    studies_data = []
    for study in studies:
        studies_data.append({"study": study, "subjects": study.subjects})

    # Also get subjects without a study
    subjects_without_study = Subject.query.filter_by(study_id=None).all()

    return render_template(
        "sujetos.html",
        studies_data=studies_data,
        subjects_without_study=subjects_without_study,
    )


@app.route("/resultados")
@login_required
def resultados():
    """
    Shows the results of registered points for a specific subject and allows download.
    ---
    parameters:
        - name: id
          in: query
          type: integer
          required: true
          description: Subject ID to show results.
    responses:
        200:
            description: Page with the registered points results.
        404:
            description: Subject not found.
    """
    subject_id = request.args.get("id", type=int)

    subject = subject_repository.get_subject_by_id(subject_id)

    if subject:
        measurements = measurement_repository.get_measurements_by_subject(
            subject_id=subject_id
        )

        points = []
        for measurement in measurements:
            if measurement.mouse_point:
                points.append(
                    {"x": measurement.mouse_point.x, "y": measurement.mouse_point.y}
                )
            if measurement.gaze_point:
                points.append(
                    {"x": measurement.gaze_point.x, "y": measurement.gaze_point.y}
                )

        return render_template("resultados.html", sujeto=subject, puntos=points)

    return "Subject not found", 404


@app.route("/visualizacion")
@login_required
def visualizacion():
    return render_template("visualizacion.html")


if __name__ == "__main__":
    db_manager.create_all()

    config_manager.print_config()

    # Check and create first user if needed
    with app.app_context():
        from db.models import User
        
        user_count = User.query.count()
        
        if user_count == 0:
            print("\n" + "=" * 60)
            print("🔐 NO USERS FOUND - CREATE FIRST USER")
            print("=" * 60 + "\n")
            
            import getpass
            
            while True:
                username = input("Username: ").strip()
                if not username:
                    print("❌ Username cannot be empty.")
                    continue
                break
            
            while True:
                password = getpass.getpass("Password: ")
                if len(password) < 4:
                    print("❌ Password must be at least 4 characters.")
                    continue
                password_confirm = getpass.getpass("Confirm password: ")
                if password != password_confirm:
                    print("❌ Passwords do not match.")
                    continue
                break
            
            user = user_repository.create_user(username=username, password=password)
            user_repository.commit()
            
            print(f"\n✅ User '{username}' created successfully!")
            print("=" * 60 + "\n")
        else:
            print(f"🔐 {user_count} user(s) found in database.")

    # Auto-create or reuse a Study from the current config
    with app.app_context():
        url_path = config_manager.get("url_path")
        img_path = config_manager.get("img_path")

        # Convert 'null' strings to None
        if url_path == "null":
            url_path = None
        if img_path == "null":
            img_path = None

        # Check if a study with this exact configuration already exists
        existing_study = None
        for study in study_repository.get_all_studies():
            if (
                study.prototype_url == url_path
                and study.prototype_image_path == img_path
            ):
                existing_study = study
                break

        if existing_study:
            active_study = existing_study
            print(
                f"📊 Using existing study: '{active_study.name}' (ID: {active_study.id})"
            )
        else:
            # Configuration has changed - ask user for study name
            print("\n" + "=" * 60)
            print("📊 New configuration detected!")
            print("=" * 60)
            if url_path:
                print(f"Prototype URL: {url_path}")
            if img_path:
                print(f"Prototype Image: {img_path}")
            print()

            study_name = input(
                "Enter a name for this study (or press Enter for auto-name): "
            ).strip()

            if not study_name:
                study_name = f"Study - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            study_description = (
                input("Enter a description (optional): ").strip()
                or "Created from configuration"
            )

            active_study = study_repository.create_study(
                name=study_name,
                description=study_description,
                prototype_url=url_path,
                prototype_image_path=img_path,
            )
            print(
                f"✅ Created new study: '{active_study.name}' (ID: {active_study.id})"
            )
            print("=" * 60 + "\n")

        # Store the active study ID in the app config for easy access
        app.config["ACTIVE_STUDY_ID"] = active_study.id

    port = config_manager.get_port(default=5001)

    app.run(debug=True, ssl_context=("cert.pem", "key.pem"), port=port)
