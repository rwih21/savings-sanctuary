from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mnysavetrack'
db = SQLAlchemy(app)

class MoneySave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_saved = db.Column(db.DateTime)
    amount_bf_saved = db.Column(db.Integer)
    amount_gf_saved = db.Column(db.Integer)
    running_total = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        # pull data from form
        date_string= request.form.get("dateSaved")
        bf_value = request.form.get("bfSaved")
        gf_value = request.form.get("gfSaved")

        # validate if its a number
        if not bf_value.isdigit() or not gf_value.isdigit():
            return "Please enter numbers only!", 400

        # convert to datetime from string
        saved_date = datetime.strptime(date_string, "%Y-%m-%d")

        current_total  = int(bf_value) + int(gf_value)

        new_entry = MoneySave(
            date_saved = saved_date,
            amount_bf_saved = int(bf_value),
            amount_gf_saved = int(gf_value),
            running_total = current_total
        )

        db.session.add(new_entry)
        db.session.commit()
        return redirect("/")

    else:
        all_savings = MoneySave.query.order_by(MoneySave.date_saved.desc()).all()
        
        total_bf = db.session.query(func.sum(MoneySave.amount_bf_saved)).scalar() or 0
        total_gf = db.session.query(func.sum(MoneySave.amount_gf_saved)).scalar() or 0
        grand_total = total_bf + total_gf

        return render_template("index.html", savings = all_savings, grand_total=grand_total)

def format_currency(value):
    if value is None:
        return "0"
    if value >= 1000:
        return f"{value / 1000:.0f}k"
    return str(value)

app.jinja_env.filters['format_currency'] = format_currency

if __name__ == "__main__":
    app.run(debug=True)