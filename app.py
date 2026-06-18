from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ==========================
# Database Model
# ==========================

class Patient(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)

    dob = db.Column(db.String(20), nullable=False)

    email = db.Column(db.String(100), nullable=False)

    glucose = db.Column(db.Float, nullable=False)

    haemoglobin = db.Column(db.Float, nullable=False)

    cholesterol = db.Column(db.Float, nullable=False)

    remarks = db.Column(db.String(200))


# ==========================
# Create Database
# ==========================

with app.app_context():
    db.create_all()


# ==========================
# AI Prediction Function
# ==========================

def predict_health(glucose, haemoglobin, cholesterol):

    if glucose > 140:
        return "High Diabetes Risk"

    elif cholesterol > 240:
        return "High Cholesterol Risk"

    elif haemoglobin < 12:
        return "Possible Anemia"

    else:
        return "Healthy"


# ==========================
# Home Page
# ==========================

@app.route("/")
def index():

    patients = Patient.query.all()

    return render_template(
        "index.html",
        patients=patients
    )


# ==========================
# Add Patient
# ==========================

@app.route("/add", methods=["GET", "POST"])
def add():

    if request.method == "POST":

        name = request.form["name"].strip()
        dob = request.form["dob"]
        email = request.form["email"].strip()

        # Validation

        if len(name) < 3:
            return "Name must be at least 3 characters"

        if "@" not in email:
            return "Invalid Email"

        try:

            glucose = float(request.form["glucose"])
            haemoglobin = float(request.form["haemoglobin"])
            cholesterol = float(request.form["cholesterol"])

        except ValueError:
            return "Please enter valid numeric values"

        if glucose < 0 or haemoglobin < 0 or cholesterol < 0:
            return "Values cannot be negative"

        remarks = predict_health(
            glucose,
            haemoglobin,
            cholesterol
        )

        patient = Patient(
            full_name=name,
            dob=dob,
            email=email,
            glucose=glucose,
            haemoglobin=haemoglobin,
            cholesterol=cholesterol,
            remarks=remarks
        )

        db.session.add(patient)
        db.session.commit()

        return redirect("/")

    return render_template("add.html")


# ==========================
# Edit Patient
# ==========================

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    patient = Patient.query.get_or_404(id)

    if request.method == "POST":

        patient.full_name = request.form["name"]
        patient.dob = request.form["dob"]
        patient.email = request.form["email"]

        patient.glucose = float(request.form["glucose"])
        patient.haemoglobin = float(request.form["haemoglobin"])
        patient.cholesterol = float(request.form["cholesterol"])

        patient.remarks = predict_health(
            patient.glucose,
            patient.haemoglobin,
            patient.cholesterol
        )

        db.session.commit()

        return redirect("/")

    return render_template(
        "edit.html",
        patient=patient
    )


# ==========================
# Delete Patient
# ==========================

@app.route("/delete/<int:id>")
def delete(id):

    patient = Patient.query.get_or_404(id)

    db.session.delete(patient)

    db.session.commit()

    return redirect("/")


# ==========================
# Run App
# ==========================

if __name__ == "__main__":
    app.run(debug=True)