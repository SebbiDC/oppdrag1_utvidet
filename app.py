from flask import Flask, render_template, request, redirect, url_for
import pymysql
from werkzeug.security import generate_password_hash

app = Flask(__name__)


def koble_til_database():
    forbindelse = pymysql.connect(
        host="10.200.15.17",
        user="sebbicd",
        password="4646",
        database="oppdrag1_utvidet",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )
    return forbindelse


@app.route("/")
def index():
    return render_template("index.html", title="Home")


@app.route("/om")
def om():
    return render_template("om.html", title="Noe")


@app.route("/show_db")
def show_db():
    with (
        koble_til_database() as forbindelse,
        forbindelse.cursor() as peker,
    ):
        sql = (
            "SELECT bruker_id, fornavn, etternavn, epost, telefon, bosted, vert "
            "FROM bruker ORDER BY fornavn"
        )
        peker.execute(sql)
        brukere = peker.fetchall()

        sql = "SELECT spill_id, navn, spillere FROM brettspill ORDER BY navn"
        peker.execute(sql)
        spill = peker.fetchall()

    return render_template("show_db.html", title="Database",
                           brukere=brukere, spill=spill)


@app.route("/registrering")
def registrering():
    with (
        koble_til_database() as forbindelse,
        forbindelse.cursor() as peker,
    ):
        sql = "SELECT spill_id, navn FROM brettspill ORDER BY navn"
        peker.execute(sql)
        spill = peker.fetchall()

    return render_template("registrering.html", title="Registrering", spill=spill)


@app.route("/lagre", methods=["POST"])
def lagre_bruker():
    fornavn = request.form["fornavn"]
    etternavn = request.form["etternavn"]
    epost = request.form["epost"]
    telefon = request.form["telefon"]
    bosted = request.form["bosted"]
    passord_hash = generate_password_hash(request.form["passord"])
    vert = request.form.get("vert") == "on"
    spill_id = request.form.get("spill_id") or None

    with (
        koble_til_database() as forbindelse,
        forbindelse.cursor() as peker,
    ):
        sql = (
            "INSERT INTO bruker "
            "(fornavn, etternavn, epost, passord_hash, telefon, bosted, vert) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        verdier = (fornavn, etternavn, epost, passord_hash, telefon, bosted, vert)
        peker.execute(sql, verdier)

        sql = (
            "UPDATE vert SET spill_id = %s "
            "WHERE vert_id = (SELECT vert_id FROM bruker WHERE epost = %s)"
        )
        peker.execute(sql, (spill_id, epost))
        forbindelse.commit()

    return redirect(url_for("show_db"))


if __name__ == "__main__":
    app.run(debug=True)