from flask import Flask, request, render_template
import sqlite3
import hashlib

app = Flask(__name__)


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
@app.route('/registracia', methods=['POST'])
def registracia_trenera():
    meno = request.form['meno']
    priezvisko = request.form['priezvisko']
    specializacia = request.form['specializacia']
    telefon = request.form['telefon']
    heslo = request.form['heslo']

    # Hashovanie hesla
    heslo_hash = hashlib.sha256(heslo.encode()).hexdigest()

    # Zápis do databázy
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Treneri (Meno, Priezvisko, Specializacia, Telefon, Heslo) VALUES (?, ?, ?, ?, ?)", 
                   (meno, priezvisko, specializacia, telefon, heslo_hash))
    conn.commit()
    conn.close()

    # Hlásenie o úspešnej registrácii
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
    conn = pripoj_db()
    cursor= conn.cursor()

    cursor.execute("SELECT * FROM Kurzy")
    kurzy = cursor.fetchall()

    conn.close()

    
    return render_template("kurzy.html", kurzy = kurzy)



@app.route("/miesta")
def zobraz_miesta():
        conn = pripoj_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Miesta")
        miesta = cursor.fetchall()

        conn.close()

        return render_template("miesta.html", miesta = miesta)


@app.route("/kapacita") 
def zobraz_kapacitu():
        conn = pripoj_db()
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(Max_pocet_ucastnikov) FROM Kurzy WHERE Nazov_kurzu LIKE 'P%'")
        kapacita = cursor.fetchall()

        conn.close()

        return render_template("kapacita.html", kapacita = kapacita)






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