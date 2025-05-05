from flask import Flask, request, render_template
import sqlite3
import hashlib

app = Flask(__name__)


def pripoj_db():
    conn = sqlite3.connect("kurzy_a_treneri.db")
    return conn


@app.route('/')  # API endpoint
def index():
    # Úvodná stránka s dvoma tlačidami ako ODKAZMI na svoje stránky - volanie API nedpointu
    return '''
        <h1>Výber z databázy</h1>
        <a href="/registracia"><button>registracia trenera</button></a>
        <a href="/sifrovanie"><button>registracia kurzu</button></a>
        <a href="/kurzyAtreneri"><button>treneri a ich kurzy</button></a>
        <a href="/kurzy"><button>vsetky kurzy</button></a>
        <a href="/miesta"><button>vsetky miesta</button></a>
        <a href="/kapacita"><button>sucet max. kapacity kurzov na "P"</button></a>
        <hr>
        '''





# STRÁNKA S FORMULÁROM NA REGISTRÁCIU TRÉNERA. Vráti HTML formulár s elementami
# Metóda je GET. (Predtým sme metódu nedefinovali. Ak žiadnu neuvedieme, automaticky je aj tak GET)
@app.route('/registracia', methods=['GET'])
def registracia_form():
    return '''
        <h2>Registrácia trénera</h2>
        <form action="/registracia" method="post">
            <label>Meno:</label><br>
            <input type="text" name="meno" required><br><br>

            <label>Priezvisko:</label><br>
            <input type="text" name="priezvisko" required><br><br>

            <label>Špecializácia:</label><br>
            <input type="text" name="specializacia" required><br><br>

            <label>Telefón:</label><br>
            <input type="text" name="telefon" required><br><br>

            <label>Heslo:</label><br>
            <input type="password" name="heslo" required><br><br>

            <button type="submit">Registrovať</button>
        </form>
        <hr>
        <a href="/">Späť</a>
    '''


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
    return '''
        <h2>Tréner bol úspešne zaregistrovaný!</h2>
        <hr>
        <a href="/">Späť</a>
    '''


@app.route('/kurzyAtreneri')
def zobraz_vysledok():
      conn = pripoj_db()
      cursor = conn.cursor()

      cursor.execute("SELECT * FROM VSETCI_TRENERI_A_ICH_KURZY")
      vysledok = cursor.fetchall()

      conn.close()
      vystup = "<h2>Zoznam trenerov a ich kurzov:</h2>"
      for vypis in vysledok:
        vystup += f"<p>{vypis}</p>"
      vystup += '<a href="/">Späť</a>' 
      return vystup 


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

        vystup = "<h2>Zoznam miest:</h2>"
        for miesto in miesta:
                vystup += f"<p>{miesto}</p>"
        vystup += '<a href="/">Späť</a>'
        return vystup 


@app.route("/kapacita") 
def zobraz_kapacitu():
        conn = pripoj_db()
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(Max_pocet_ucastnikov) FROM Kurzy WHERE Nazov_kurzu LIKE 'P%'")
        kapacita = cursor.fetchall()

        conn.close()

        vystup = "<h2>sucet max. kapacity kurzov na ""P"":</h2>"
        for capacita in kapacita:
                vystup += f"<p>{capacita}</p>"
        vystup += '<a href="/">Späť</a>'
        return vystup






@app.route('/sifrovanie', methods=['GET'])
def vkladanie_kurzov():
    return '''
        <h2>Vkladanie kurzu</h2>
        <form action="/sifrovanie" method="post">
            <label>Nazov:</label><br>
            <input type="text" name="Nazov_kurzu" required><br><br>

            <label>Typ športu:</label><br>
            <input type="text" name="Typ_sportu" required><br><br>

            <label>ID kurzu:</label><br>
            <input type="text" name="ID_kurzu" required><br><br>

            <label>Max. počet účastníkov:</label><br>
            <input type="text" name="Max_pocet_ucastnikov" required><br><br>

            <label>ID trenera:</label><br>
            <input type="text" name="ID_trenera" required><br><br>

            <button type="submit">Vložiť</button>
        </form>
        <hr>
        <a href="/">Späť</a>
    '''


@app.route('/sifrovanie', methods=['POST'])
def vlozenie_kurzu():
    

    def sifra(text):
        a = 5
        b = 8
        text = text.upper()
        sifrovany_text = ""
        for char in text:
            if char.isalpha():
                x = ord(char) - ord('A')
                sifrovane_pismeno = (a * x + b) % 26
                sifrovany_text += chr(sifrovane_pismeno + ord('A'))
            else:
                sifrovany_text += char 
        return sifrovany_text

    nazov_kurzu = sifra(request.form.get('Nazov_kurzu', ''))

    typ_sportu = sifra(request.form.get('Typ_sportu',''))
    ID_kurzu = request.form['ID_kurzu']
    max_pocet_ucastnikov = request.form['Max_pocet_ucastnikov']
    ID_trenera = request.form['ID_trenera']

    # Zápis do databázy
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Kurzy (ID_kurzu, Nazov_kurzu, Typ_sportu, Max_pocet_ucastnikov, ID_trenera) VALUES (?, ?, ?, ?, ?)", 
                   (ID_kurzu, nazov_kurzu, typ_sportu, max_pocet_ucastnikov, ID_trenera))
    print("Do DB ide nazov:", nazov_kurzu)
    conn.commit()
    conn.close()

    # Hlásenie o úspešnej registrácii
    return '''
        <h2>Kurz bol úspešne zaregistrovaný!</h2>
        <hr>
        <a href="/">Späť</a>
    '''

if __name__ == '__main__':
    app.run(debug=True)