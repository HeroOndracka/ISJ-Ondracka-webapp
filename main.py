from flask import Flask, request, render_template
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import hashlib
import os
app = Flask(__name__,instance_relative_config=True)

db_path = os.path.join(app.instance_path, "kurzy_a_treneri.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}".replace("\\","//")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
#--------------------------------------------------------------
class Kurz(db.Model):
    __tablename__ = "Kurzy"
    ID_Kurzu = db.Column(db.Integer, primary_key = True)
    Nazov_kurzu = db.Column(db.String, nullable = False)
    Typ_sportu = db.Column(db.String)
    Max_pocet_ucastnikov = db.Column(db.Integer)
    ID_trenera = db.Column(db.Integer)

    def __repr__(self):
         return f"Kurz {self.Nazov_kurzu}"


class Miesto(db.Model):
    __tablename__ = "Miesta"
    ID_miesta = db.Column(db.Integer, primary_key = True)
    Nazov_miesta = db.Column(db.String, nullable = False)
    Adresa = db.Column(db.String)
    Kapacita = db.Column(db.Integer)

    def __repr__(self):
         return f"Miesto {self.Nazov_miesta}"

class Trener(db.Model):
    __tablename__ = "Treneri"
    
    ID_trenera = db.Column(db.Integer, primary_key=True)
    Meno = db.Column(db.String, nullable=False)
    Priezvisko = db.Column(db.String, nullable=False)
    Specializacia = db.Column(db.String)
    Telefon = db.Column(db.String)
    Heslo = db.Column(db.String, nullable=False)  # hashované heslo

    def __repr__(self):
        return f"<Trener {self.Meno} {self.Priezvisko}>"


#-----------------------------------------------------------
def pripoj_db():
    conn = sqlite3.connect("kurzy_a_treneri.db")
    return conn


@app.route('/')  # API endpoint
def index():
    # Úvodná stránka s tlačidami ako ODKAZMI na svoje stránky - volanie API nedpointu
    return render_template("uvodna.stranka.html")





# STRÁNKA S FORMULÁROM NA REGISTRÁCIU TRÉNERA. Vráti HTML formulár s elementami
# Metóda je GET. (Predtým sme metódu nedefinovali. Ak žiadnu neuvedieme, automaticky je aj tak GET)
@app.route('/registracia', methods=['GET'])
def registracia_form():
    return render_template("registraciaGET.html")


# API ENDPOINT NA SPRACOVANIE REGISTRÁCIE. Mapuje sa na mená elementov z formulára z predošlého requestu (pomocou request.form[...])
# Pozor - metóda je POST
from werkzeug.security import generate_password_hash  # lepšie ako hashlib

@app.route('/registracia', methods=['POST'])
def registracia_trenera():
    meno = request.form['meno']
    priezvisko = request.form['priezvisko']
    specializacia = request.form['specializacia']
    telefon = request.form['telefon']
    heslo = request.form['heslo']

    # Hashovanie hesla (lepší spôsob)
    heslo_hash = generate_password_hash(heslo)

    # Vytvorenie nového objektu Trener
    novy_trener = Trener(
        Meno=meno,
        Priezvisko=priezvisko,
        Specializacia=specializacia,
        Telefon=telefon,
        Heslo=heslo_hash
    )

    # Pridanie do DB
    db.session.add(novy_trener)
    db.session.commit()

    return render_template("registraciaPOST.html")



@app.route('/kurzyAtreneri')
def zobraz_vysledok():
      conn = pripoj_db()
      cursor = conn.cursor()

      cursor.execute("SELECT * FROM VSETCI_TRENERI_A_ICH_KURZY")
      vysledok = cursor.fetchall()

      conn.close()

      return render_template("kurzyAtreneri.html", vysledok = vysledok)


@app.route("/kurzy")
def zobraz_kurzy():
    kurzy = Kurz.query.all()
    return render_template("kurzy.html", kurzy = kurzy)

@app.route("/miesta")
def zobraz_miesta():
    miesta = Miesto.query.all()
    return render_template("miesta.html", miesta = miesta)

@app.route("/kapacita")
def zobraz_kapacitu():
    kapacita = db.session.query(func.sum(Kurz.Max_pocet_ucastnikov))\
                .filter(Kurz.Nazov_kurzu.like("P%")).scalar()
    return render_template("kapacita.html", kapacita=kapacita)






@app.route('/sifrovanie', methods=['GET'])
def vkladanie_kurzov():
    return render_template("kurzyGET.html")

@app.route('/sifrovanie', methods=['POST'])
@app.route('/sifrovanie', methods=['POST'])
def vlozenie_kurzu():
    # Načítanie dát z formulára
    nazov_kurzu = request.form.get('Nazov_kurzu', '')
    typ_sportu = request.form.get('Typ_sportu', '')
    ID_kurzu = request.form['ID_kurzu']
    max_pocet_ucastnikov = request.form['Max_pocet_ucastnikov']
    ID_trenera = request.form['ID_trenera']

    # Debug výpis
    print("Do DB ide kurz:", nazov_kurzu)

    # Bezpečný zápis do databázy
    try:
        with sqlite3.connect("kurzy_a_treneri.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Kurzy (ID_kurzu, Nazov_kurzu, Typ_sportu, Max_pocet_ucastnikov, ID_trenera)
                VALUES (?, ?, ?, ?, ?)""",
                (ID_kurzu, nazov_kurzu, typ_sportu, max_pocet_ucastnikov, ID_trenera)
            )
            conn.commit()
    except sqlite3.IntegrityError as e:
        return f"⚠️ Chyba pri ukladaní do databázy: {e}"  # napr. duplicate ID
    except Exception as e:
        return f"❌ Neočakávaná chyba: {e}"

    # Všetko OK → zobraz POST šablónu
    return render_template("kurzyPOST.html")


if __name__ == '__main__':
    app.run(debug=True)