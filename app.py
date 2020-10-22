import bcrypt
from datetime import date, timedelta, datetime
from flask import Flask, render_template, url_for, request, redirect, session
from db_operations import *
from flask_mysqldb import MySQL, MySQLdb
from databaseConnection import getCredentials

myHost, myUser, myPasswd, myDatabase, port = getCredentials()

app = Flask(__name__)
app.config['MYSQL_HOST'] = myHost
app.config['MYSQL_USER'] = myUser
app.config['MYSQL_PASSWORD'] = myPasswd
app.config['MYSQL_DB'] = myDatabase
app.config['MYSQL_PORT'] = port
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)
app.secret_key = '748fdmf**jnxhdelndf'

@app.route('/', methods=['POST', 'GET'])
def index():
    login = session.get('login')
    if not login:
        return redirect('/main')
    else:
        return redirect('/panel')

@app.route('/main', methods=['GET'])
def main():
    return render_template('/main.html')

@app.route('/panel', methods=['POST', 'GET'])
def panel():
    login = session.get('login')
    if not login:
        return redirect('/main')
    else:
        length = len(login)
        if length == 11 and login[0] != 'L' and login[0] != 'P' and login[0] != 'A':
            return redirect('/dawca')
        elif length == 8 and login[0] == 'L': #L+PWZ
            return redirect('/lekarz')
        elif length == 8 and login[0] == 'P': #P+PWZ
            return redirect('/pielegniarka')
        elif length == 8 and login[0] == 'A': #A+login 
            return redirect('/admin')
        else:
            session['login'] = ""
            return redirect('/')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        pesel = request.form['pesel']
        if (len(pesel) != 11 or not pesel.isdigit()):
            return render_template('register.html', info="Nieprawidłowy numer PESEL")
        haslo = request.form['haslo'].encode('utf-8')
        if len(haslo) == 0:
            return render_template('register.html', info="Nieprawidłowe hasło")
        hash_haslo = bcrypt.hashpw(haslo, bcrypt.gensalt())
        imie = request.form['imie']
        imie2 = ""
        imie2 = request.form['imie2']
        nazwisko = request.form['nazwisko']
        rodowe = request.form['rodowe']
        plec = request.form['plec']
        data_ur = request.form['data_ur']
        obywatel = request.form['obywatel']
        adres = request.form['adres']
        tel = request.form['tel']
        email = request.form['email']
        legitymacja = ""
        legitymacja = request.form['legitymacja']
        try:
            registerDawca(mysql, pesel, imie, imie2, nazwisko, rodowe, data_ur, adres, tel, email, hash_haslo, plec, legitymacja, obywatel)
        except:
            return render_template('main.html', info="Rejestracja nieudana!")
        return render_template('main.html', info="Rejestracja przebiegła pomyślnie")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form['login']
        haslo = request.form['haslo'].encode('utf-8')
        if login[0] == 'P':
            user = getHasloP(mysql, login)
            if user:
                if bcrypt.checkpw(haslo, user['haslo'].encode('utf-8')):
                    session['login'] = "P" + str(user['nr_pwzp'])
                    return redirect("/pielegniarka")
                else:
                    return redirect('/login')
            else:
                return redirect('/login')
        elif login[0] == 'L':
            user = getHasloL(mysql, login)
            if user:
                if bcrypt.checkpw(haslo, user['haslo'].encode('utf-8')):
                    session['login'] = "L" + str(user['nr_pwzl'])
                    return redirect("/lekarz")
                else:
                    return redirect('/login')
            else:
                return redirect('/login')
        elif login[0] == 'A':
            user = getHasloA(mysql, login)
            if user:
                if bcrypt.checkpw(haslo, user['haslo'].encode('utf-8')):
                    session['login'] = user['login']
                    return redirect('/admin')
                else:
                    return redirect('/login')
            else:
                return redirect('/login')        
        else:
            user = getHaslo(mysql, login)
            if user:
                if bcrypt.checkpw(haslo, user['haslo'].encode('utf-8')):
                    session['login'] = user['pesel']
                    return redirect("/dawca")
                else:
                    return redirect('/login')
            else:
                return redirect('/login')
    else:
        return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

### DAWCA ###
@app.route('/dawca', methods=['POST', 'GET'])
def dawca():
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log == 'L' or log == 'P' or log == 'A':
        return redirect('/panel')
    if request.method == "GET":
        ## obliczanie kolejnych możliwych donacji
        login = session['login']
        ostatniaDonacjaRow = pobierzInformacjeOstatniejDonacji(mysql, login)
        if ostatniaDonacjaRow:
            dataOstatnia = ostatniaDonacjaRow['data']
            rodzajOstatnia = ostatniaDonacjaRow['rodzaj_pobrania']
            iloscOstatnia = ostatniaDonacjaRow['ilosc']
            kolejneDonacje = obliczKolejneDonacje(dataOstatnia, rodzajOstatnia)
            for i in kolejneDonacje:
                if type(kolejneDonacje[i]) == str:
                    continue
                if kolejneDonacje[i] <= date.today():
                    kolejneDonacje[i] = "Można!"   
        else:
            dataOstatnia = "Nie zarejestrowano żadnej donacji"
            rodzajOstatnia = ""
            iloscOstatnia = 0
            kolejneDonacje = ""
        
        #przeliczanie składników krwi na krew pełną
        donacje = pobierzDonacjeDawcy(mysql, login)
        plec = pobierzPlecDawcy(mysql, login)
        if donacje:
            KP = obliczSumeKP(donacje)
            tytul = sprawdźTytul(plec, KP)
        else:
            KP = 0
            tytul = "-"
        return render_template("dawca.html", dataOstatnia=dataOstatnia, rodzajOstatnia=rodzajOstatnia, iloscOstatnia=iloscOstatnia, kolejneDonacje=kolejneDonacje, KP=KP, tytul=tytul)
    else:
        pass

@app.route('/dziennikDonacji', methods=['POST', 'GET'])
def dziennikDonacji():
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log == 'L' or log == 'P' or log == 'A':
        return redirect('/panel')
    if request.method == "GET":
        login = session['login']
        dziennik = pobierzDziennikDonacji(mysql, login)
        return render_template("dziennikDonacji.html", dziennik=dziennik)

@app.route('/dziennikWywiad/<string:idWizyty>', methods=['POST', 'GET'])
def dziennikWywiad(idWizyty):
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log == 'L' or log == 'P' or log == 'A':
        return redirect('/panel')
    if request.method == "GET":
        idWywiaduRow = pobierzIdWywiaduByIdWizyty(mysql, idWizyty)
        idWywiadu = idWywiaduRow['id_wywiadu']
        wywiad = pobierzWywiad(mysql, idWywiadu)
        daneLekarza = pobierzDaneLekarzaByIdWywiadu(mysql, idWywiadu)
        return render_template("dziennikWywiad.html", wywiad=wywiad, daneLekarza=daneLekarza)

@app.route('/dziennikWyniki/<string:idBadania>', methods=['POST', 'GET'])
def dziennikWyniki(idBadania):
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log == 'L' or log == 'P' or log == 'A':
        return redirect('/panel')
    if request.method == "GET":
        wyniki = pobierzWynikiBadanByIdBadania(mysql, idBadania)
        danePielegniarki = pobierzDanePielegniarkiByIdPielegniarki(mysql, wyniki['id_pielegniarki'])
        return render_template("dziennikWyniki.html", wyniki=wyniki, danePielegniarki=danePielegniarki)

@app.route('/rejestracje', methods=['GET', 'POST'])
def rejestracje():
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log == 'L' or log == 'P' or log == 'A':
        return redirect('/panel')
    if request.method == "GET":
        wizyty = pobierzRejestracje(mysql, session['login'])
        return render_template("rejestracje.html", wizyty=wizyty)

@app.route('/rejestracje/<string:idWizyty>')
def usunRejestracje(idWizyty):
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log == 'L' or log == 'P' or log == 'A':
        return redirect('/panel')
    try:
        usunRej(mysql, idWizyty)
        return redirect('/rejestracje')
    except:
        return redirect('/rejestracje')

@app.route('/ankieta/<string:idwizyty>', methods=['GET', 'POST'])
def dodajAnkiete(idwizyty):
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log == 'L' or log == 'P' or log == 'A':
        return redirect('/panel')
    if request.method == "GET":
        return render_template("ankieta.html", idwizyty=idwizyty)
    else:
        data = date.today().strftime("%Y-%m-%d")
        odpowiedzi = []
        for i in range(1, 36):
            name = 'pyt' + str(i)
            odpowiedzi.append(request.form[name])
        dodajAnk(mysql, idwizyty, odpowiedzi, data)
        return redirect('/rejestracje')

@app.route('/usunAnkiete/<string:idankiety>')
def usunAnkiete(idankiety):
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log == 'L' or log == 'P' or log == 'A':
        return redirect('/panel')
    usunAnk(mysql, idankiety)
    return redirect("/rejestracje")

@app.route('/nowaRejestracja', methods=['GET', 'POST'])
def nowaRejestracja():
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log == 'L' or log == 'P' or log == 'A':
        return redirect('/panel')
    if request.method == "GET":
        placowki = getPlacowki(mysql)
        data = date.today()
        data = data.strftime("%Y-%m-%d")
        return render_template("nowaRejestracja.html", placowki=placowki, data=data)
    else:
        data = request.form['data']
        godzina = request.form['godzina']
        placowka = request.form['placowka']     
        dodajRejestracje(mysql, session['login'], data, godzina, placowka)   
        return redirect("/rejestracje")

@app.route('/ustawieniaDawcy', methods=['GET', 'POST'])
def ustawieniaDawcy():
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log == 'L' or log == 'P' or log == 'A':
        return redirect('/panel')
    if request.method == "GET":
        login = session['login']
        dane = pobierzDaneDawcy(mysql, login)
        return render_template("ustawieniaDawcy.html", dane=dane)
    else:
        login = session['login']
        imie = request.form['imie']
        imie2 = request.form['imie2']
        nazwisko = request.form['nazwisko']
        rodowe = request.form['rodowe']
        plec = request.form['plec']
        data_ur = request.form['data_ur']
        obywatel = request.form['obywatel']
        adres = request.form['adres']
        tel = request.form['tel']
        email = request.form['email']
        legitymacja = request.form['legitymacja']
        aktualizujDane(mysql, login, imie, imie2, nazwisko, rodowe, plec, data_ur, obywatel, adres, tel, email, legitymacja)
        haslo = request.form['haslo'].encode('utf-8')
        if len(haslo) > 0:
            hash_haslo = bcrypt.hashpw(haslo, bcrypt.gensalt())
            aktualizujHaslo(mysql, login, hash_haslo)
    return redirect('/panel')
### endDAWCA ###

### LEKARZ ###
@app.route('/lekarz', methods=['GET'])
def lekarz():
    if not session.get('login'):
        return redirect('/main')
    if session['login'][0] != 'L':
        return redirect('/panel')
    if request.method == "GET":
        login = session['login']
        idPlacowki = pobierzMiejscePracy(mysql, login)
        miejsce = getNazwePlacowkiById(mysql, idPlacowki)
        data = date.today().strftime("%Y-%m-%d")
        wizyty = pobierzRejestracjeDlaLekarza(mysql, idPlacowki, data)
        return render_template("lekarz.html", miejsce=miejsce, wizyty=wizyty, data=data)

@app.route('/ustawieniaLekarza', methods=['GET', 'POST'])
def ustawieniaLekarza():
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log != 'L':
        return redirect('/panel')
    if request.method == "GET":
        login = session['login']
        dane = pobierzDaneLekarza(mysql, login)
        return render_template("ustawieniaLekarza.html", dane=dane)
    else:
        login = session['login']
        imie = request.form['imie']
        imie2 = request.form['imie2']
        nazwisko = request.form['nazwisko']
        data_ur = request.form['data_ur']
        adres = request.form['adres']
        tel = request.form['tel']
        email = request.form['email']
        specjalizacja = request.form['spec']
        aktualizujDaneLekarza(mysql, login, imie, imie2, nazwisko, data_ur, adres, tel, email, specjalizacja)
        haslo = request.form['haslo'].encode('utf-8')
        if len(haslo) > 0:
            hash_haslo = bcrypt.hashpw(haslo, bcrypt.gensalt())
            aktualizujHasloLekarza(mysql, login, hash_haslo)
    return redirect('/panel')

@app.route('/wynikiAnkiety/<string:idAnkiety>', methods=['POST', 'GET'])
def wynikiAnkiety(idAnkiety):
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log != 'L' and log != 'P':
        return redirect('/panel')
    if request.method == "GET":
        ankieta = pobierzAnkieteDawcy(mysql, idAnkiety)
        pesel = pobierzPeselByIdAnkiety(mysql, idAnkiety)
        return render_template("wynikiAnkiety.html", pesel=pesel, ankieta=ankieta)

@app.route('/wywiad/<string:idWizyty>', methods=['POST', 'GET'])
def wywiad(idWizyty):
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log != 'L':
        return redirect('/panel')
    if request.method == "GET":
        hb = pobierzHemoglobine(mysql, idWizyty)
        return render_template("wywiad.html", hb=hb, idWizyty=idWizyty)
    else:
        wzrost = request.form['wzrost']
        waga = request.form['waga']
        temperatura = request.form['temperatura']
        cisnienie = request.form['cisnienie']
        tetno = request.form['tetno']
        wezly_chlonne = request.form['wezly_chlonne']
        skora = request.form['skora']
        uwagi = request.form['uwagi']
        akceptacja = request.form['akceptacja']
        login = session['login']
        dodajWywiad(mysql, login, idWizyty, wzrost, waga, temperatura, cisnienie, tetno, wezly_chlonne, skora, uwagi, akceptacja)
        return redirect('/panel')
        
@app.route('/zobaczWywiad/<string:idWywiadu>', methods=['POST', 'GET'])
def zobaczWywiad(idWywiadu):
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log != 'L':
        return redirect('/panel')
    if request.method == "GET":
        wywiad = pobierzWywiad(mysql, idWywiadu)
        hb = pobierzHemoglobine(mysql, wywiad['id_wizyty'])
        return render_template("zobaczWywiad.html", wywiad=wywiad, hb=hb)
    else:
        wzrost = request.form['wzrost']
        waga = request.form['waga']
        temperatura = request.form['temperatura']
        cisnienie = request.form['cisnienie']
        tetno = request.form['tetno']
        wezly_chlonne = request.form['wezly_chlonne']
        skora = request.form['skora']
        uwagi = request.form['uwagi']
        akceptacja = request.form['akceptacja']
        aktualizujWywiad(mysql, idWywiadu, wzrost, waga, temperatura, cisnienie, tetno, wezly_chlonne, skora, uwagi, akceptacja)
    return redirect('/panel')
### endLEKARZ ###

### PIELEGNIARKA ###
@app.route('/pielegniarka', methods=['GET'])
def pielegniarka():
    if not session.get('login'):
        return redirect('/main')
    if session['login'][0] != 'P':
        return redirect('/panel')
    if request.method == "GET":
        return render_template("pielegniarka.html")

@app.route('/zarzadzanieDawcami', methods=['POST', 'GET'])
def zarzadzanieDawcami():
    if not session.get('login'):
        return redirect('/main')
    if session['login'][0] != 'P':
        return redirect('/panel')
    if request.method == "GET":
        czyPost = 0
        return render_template("zarzadzanieDawcami.html",czyPost=czyPost)
    else:
        pesel = request.form['wyszukaj']
        czyPost = 1
        dawca = pobierzDaneDawcy(mysql, pesel)
        return render_template("zarzadzanieDawcami.html", dawca=dawca, czyPost=czyPost, pesel=pesel)

@app.route('/dodajDawce', methods=['POST', 'GET'])
def dodajDawce():
    if not session.get('login'):
        return redirect('/main')
    if session['login'][0] != 'P':
        return redirect('/panel')
    if request.method == "GET":
        return render_template("dodajDawce.html")
    else:
        pesel = request.form['pesel']
        if (len(pesel) != 11 or not pesel.isdigit()):
            return render_template('dodajDawce.html', info="Nieprawidłowy numer PESEL")
        haslo = request.form['haslo'].encode('utf-8')
        hash_haslo = bcrypt.hashpw(haslo, bcrypt.gensalt())
        imie = request.form['imie']
        imie2 = ""
        imie2 = request.form['imie2']
        nazwisko = request.form['nazwisko']
        rodowe = request.form['rodowe']
        plec = request.form['plec']
        data_ur = request.form['data_ur']
        obywatel = request.form['obywatel']
        adres = request.form['adres']
        tel = request.form['tel']
        email = request.form['email']
        legitymacja = ""
        legitymacja = request.form['legitymacja']
        registerDawca(mysql, pesel, imie, imie2, nazwisko, rodowe, data_ur, adres, tel, email, hash_haslo, plec, legitymacja, obywatel)
        return redirect('/zarzadzanieDawcami')

@app.route('/nowaRejestracja/<string:pesel>', methods=['POST', 'GET'])
def nowaRejestracjaByPielegniarka(pesel):
    if not session.get('login'):
        return redirect('/main')
    if session['login'][0] != 'P':
        return redirect('/panel')
    login = session['login']
    id_placowki = pobierzMiejscePracyPielegniarki(mysql, login)
    if request.method == "GET":
        login = session['login']
        miejsce_pracy = getNazwePlacowkiById(mysql, id_placowki)
        return render_template("nowaRejestracjaByPielegniarka.html", pesel=pesel, miejsce_pracy=miejsce_pracy)
    else:
        data = request.form['data']
        godzina = request.form['godzina']
        dodajRejestracjeByPielegniarka(mysql, pesel, data, godzina, id_placowki)   
        return redirect("/zarzadzanieDawcami")

@app.route('/daneDawcy/<string:pesel>', methods=['POST', 'GET'])
def daneDawcy(pesel):
    if not session.get('login'):
        return redirect('/main')
    if session['login'][0] != 'P':
        return redirect('/panel')
    if request.method == "GET":
        dane = pobierzDaneDawcy(mysql, pesel)
        return render_template("daneDawcy.html", dane=dane)
    else:
        imie = request.form['imie']
        imie2 = request.form['imie2']
        nazwisko = request.form['nazwisko']
        rodowe = request.form['rodowe']
        plec = request.form['plec']
        data_ur = request.form['data_ur']
        obywatel = request.form['obywatel']
        adres = request.form['adres']
        tel = request.form['tel']
        email = request.form['email']
        legitymacja = request.form['legitymacja']
        aktualizujDane(mysql, pesel, imie, imie2, nazwisko, rodowe, plec, data_ur, obywatel, adres, tel, email, legitymacja)
        return redirect('/zarzadzanieDawcami')

@app.route('/ustawieniaPielegniarki', methods=['POST', 'GET'])
def ustawieniaPielegniarki():
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log != 'P':
        return redirect('/panel')
    if request.method == "GET":
        login = session['login']
        dane = pobierzDanePielegniarki(mysql, login)
        return render_template("ustawieniaPielegniarki.html", dane=dane)
    else:
        login = session['login']
        imie = request.form['imie']
        imie2 = request.form['imie2']
        nazwisko = request.form['nazwisko']
        data_ur = request.form['data_ur']
        adres = request.form['adres']
        tel = request.form['tel']
        email = request.form['email']
        aktualizujDanePielegniarki(mysql, login, imie, imie2, nazwisko, data_ur, adres, tel, email)
        haslo = request.form['haslo'].encode('utf-8')
        if len(haslo) > 0:
            hash_haslo = bcrypt.hashpw(haslo, bcrypt.gensalt())
            aktualizujHasloPielegniarki(mysql, login, hash_haslo)
        return redirect('/panel')

@app.route('/rejestracjePielegniarki', methods=['POST', 'GET'])
def rejestracjePielegniarki():
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log != 'P':
        return redirect('/panel')
    if request.method == "GET":
        czyPost = 0
        return render_template("rejestracjePielegniarki.html", czyPost=czyPost)
    else:
        data = request.form['wyszukaj_data']
        pesel = request.form['wyszukaj_pesel']
        placowka = pobierzMiejscePracyPielegniarki(mysql, session['login'])
        if len(data) > 0:
            wizyty = pobierzRejestracjeByData(mysql, placowka, data)
            czyPesel = 0
        elif len(pesel) > 0:
            wizyty = pobierzRejestracjeByPesel(mysql, placowka, pesel)
            czyPesel = 1
        else:
            return redirect("/rejestracjePielegniarki")
        czyPost = 1
        return render_template("rejestracjePielegniarki.html", wizyty=wizyty, czyPesel=czyPesel, czyPost=czyPost)

@app.route('/usunRejestracjePielegniarki/<string:idWizyty>')
def usunRejestracjePielegniarki(idWizyty):
    if not session.get('login'):
        return redirect('/main')
    if session['login'][0] != 'P':
        return redirect('/panel')
    usunRejPielegniarki(mysql, idWizyty)
    return redirect('/rejestracjePielegniarki')

@app.route('/dodajAnkiete/<string:idWizyty>', methods=['GET', 'POST'])
def dodajAnkieteByPielegniarka(idWizyty):
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log != 'P':
        return redirect('/panel')
    if request.method == "GET":
        return render_template("dodajAnkiete.html", idWizyty=idWizyty)
    else:
        data = date.today().strftime("%Y-%m-%d")
        odpowiedzi = []
        for i in range(1, 36):
            name = 'pyt' + str(i)
            odpowiedzi.append(request.form[name])
        dodajAnk(mysql, idWizyty, odpowiedzi, data)
        return redirect('/rejestracjePielegniarki')

@app.route('/dodajBadanie/<string:idWizyty>', methods=['GET', 'POST'])
def dodajBadanie(idWizyty):
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log != 'P':
        return redirect('/panel')
    if request.method == "GET":
        idWywiaduRow = pobierzIdWywiaduByIdWizyty(mysql, idWizyty)
        if idWywiaduRow:
            czyWywiad = 1
        else:
            czyWywiad = 0
        grupaKrwiRow = pobierzGrupeKrwiByIdWizyty(mysql, idWizyty)
        if grupaKrwiRow:
            grupaKrwi = grupaKrwiRow['gr_krwi']
        grupyKrwi = pobierzGrupyKrwi(mysql)

        idBadaniaRow = pobierzIdBadaniaByIdWizyty(mysql, idWizyty)
        if idBadaniaRow:
            wyniki = pobierzWynikiBadanByIdBadania(mysql, idBadaniaRow['id_badania'])
            czyWyniki = 1
            if czyWywiad:
                akceptacja = pobierzAkceptacjaWywiadByIdWizyty(mysql, idWizyty)
                return render_template("dodajBadanie.html", idWizyty=idWizyty, czyWywiad=czyWywiad, grupaKrwi=grupaKrwi, grupyKrwi=grupyKrwi, wyniki=wyniki, czyWyniki=czyWyniki, akceptacja=akceptacja)
            else:
                return render_template("dodajBadanie.html", idWizyty=idWizyty, czyWywiad=czyWywiad, grupaKrwi=grupaKrwi, grupyKrwi=grupyKrwi, wyniki=wyniki, czyWyniki=czyWyniki)
        else:
            czyWyniki = 0
            return render_template("dodajBadanie.html", idWizyty=idWizyty, czyWywiad=czyWywiad, grupaKrwi=grupaKrwi, grupyKrwi=grupyKrwi, czyWyniki=czyWyniki)
    else:
        grKrwiRow = pobierzGrupeKrwiFromDawcaByIdWizyty(mysql, idWizyty)
        print(grKrwiRow)
        if grKrwiRow['gr_krwi'] == None:
            grKrwi = request.form['grupa_krwi']
            print(grKrwi)
            if not grKrwi == "nie_oznaczono":
                dodajGrupeKrwiByIdWizyty(mysql, idWizyty, grKrwi)
        hb = request.form['hb']
        idBadaniaRow = pobierzIdBadaniaByIdWizyty(mysql, idWizyty)
        if idBadaniaRow:
            aktualizujHemoglobine(mysql, idWizyty, hb)

            idWywiaduRow = pobierzIdWywiaduByIdWizyty(mysql, idWizyty)
            if idWywiaduRow:
                czyWywiad = 1
            else:
                czyWywiad = 0

            if czyWywiad:
                akceptacja = pobierzAkceptacjaWywiadByIdWizyty(mysql, idWizyty)
                if akceptacja != "NIE":
                    morfologiaRow = pobierzIdMorfologiByIdBadania(mysql, idBadaniaRow['id_badania'])
                    parametry = {}
                    parametry["ht"] = request.form['ht']
                    parametry["rbc"] = request.form['rbc']
                    parametry["wbc"] = request.form['wbc']
                    parametry["plt"] = request.form['plt']
                    parametry["mch"] = request.form['mch']
                    parametry["mchc"] = request.form['mchc']
                    parametry["mcv"] = request.form['mcv']
                    parametry["ne"] = request.form['ne']
                    parametry["eo"] = request.form['eo']
                    parametry["ba"] = request.form['ba']
                    parametry["ly"] = request.form['ly']
                    parametry["mo"] = request.form['mo']
                    parametry["alat"] = request.form['alat']
                    if morfologiaRow:
                        aktualizujMorfologie(mysql, morfologiaRow['id_morfologii'], parametry)
                    else:
                        dodajMorfologie(mysql, idBadaniaRow['id_badania'], parametry)
                    
                    wirusologiaRow = pobierzIdWirusologiByIdBadania(mysql, idBadaniaRow['id_badania'])
                    hbs = request.form['hbs']
                    hiv = request.form['hiv']
                    hcv = request.form['hcv']
                    rna_hcv = request.form['rna_hcv']
                    rna_hiv = request.form['rna_hiv']
                    dna_hbv = request.form['dna_hbv']
                    kila = request.form['kila']
                    if wirusologiaRow:
                        aktualizujWirusologie(mysql, wirusologiaRow['id_wirusologii'], hbs, hiv, hcv, rna_hcv, rna_hiv, dna_hbv, kila)
                    else:
                        dodajWirusologie(mysql, idBadaniaRow['id_badania'], hbs, hiv, hcv, rna_hcv, rna_hiv, dna_hbv, kila)
        else:
            login = session['login']
            idPielegniarki = pobierzIdPielegniarki(mysql, login)
            dodajHemoglobine(mysql, idWizyty, idPielegniarki, hb)
        return redirect("/rejestracjePielegniarki")        

@app.route('/zobaczWywiadByPielegniarka/<string:idWywiadu>', methods=['POST', 'GET'])
def zobaczWywiadByPielegniarka(idWywiadu):     
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log != 'P':
        return redirect('/panel')
    if request.method == "GET":
        wywiad = pobierzWywiad(mysql, idWywiadu)
        return render_template("zobaczWywiadByPielegniarka.html", wywiad=wywiad)

@app.route('/dodajDonacje/<string:idWizyty>', methods=['POST', 'GET'])
def dodajPobranie(idWizyty): 
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log != 'P':
        return redirect('/panel')
    if request.method == "GET":
        pobrania = pobierzRodzajePobran(mysql)
        pesel = pobierzPeselByIdWizyty(mysql, idWizyty)
        return render_template("dodajDonacje.html", pobrania=pobrania, pesel=pesel, idWizyty=idWizyty)
    else: 
        godz = request.form['godz_donacji']
        rodzaj_pobrania = request.form['rodzaj_pobrania']
        ilosc = request.form['ilosc']
        pesel = pobierzPeselByIdWizyty(mysql, idWizyty)
        idBadaniaRow =  pobierzIdBadaniaByIdWizyty(mysql, idWizyty)
        idBadania = idBadaniaRow['id_badania']
        dodajDonacje(mysql, idBadania, pesel, godz, rodzaj_pobrania, ilosc)
        return redirect("/rejestracjePielegniarki")

@app.route('/zobaczDonacje/<string:idWizyty>', methods=['POST', 'GET'])
def zobaczDonacje(idWizyty): 
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log != 'P':
        return redirect('/panel')
    if request.method == "GET":
        donacja = pobierzDonacje(mysql, idWizyty)
        return render_template("zobaczDonacje.html", donacja=donacja, idWizyty=idWizyty)
    else:
        aktualizujDonacje(mysql, idWizyty)
        return redirect("/zobaczDonacje/"+idWizyty)

@app.route('/zasobyKrwi', methods=['POST', 'GET'])
def zasobyKrwi():
    if not session.get('login'):
        return redirect('/main')
    log = session['login'][0]
    if log != 'P':
        return redirect('/panel')
    if request.method == "GET":
        login = session['login']
        idPlacowki = pobierzMiejscePracyPielegniarki(mysql, login)
        nazwaPlacowki = getNazwePlacowkiById(mysql, idPlacowki)
        krewPelna = pobierzIloscKrwiPelnejByGrupy(mysql, idPlacowki)
        skladnikiKrwi = pobierzIloscSkladnikowKrwiByRodzaj(mysql, idPlacowki)
        try:
            int(skladnikiKrwi['Krwinki czerwone 1j.'])
            try:
                int(skladnikiKrwi['Krwinki czerwone 2j.'])
                krwinkiCzerwone = skladnikiKrwi['Krwinki czerwone 1j.'] + skladnikiKrwi['Krwinki czerwone 2j.']
            except:
                krwinkiCzerwone = skladnikiKrwi['Krwinki czerwone 1j.']
        except:
            try:
                int(skladnikiKrwi['Krwinki czerwone 2j.'])
                krwinkiCzerwone = skladnikiKrwi['Krwinki czerwone 2j.']
            except:
                krwinkiCzerwone = ""
        return render_template("zasobyKrwi.html", nazwaPlacowki=nazwaPlacowki , krewPelna=krewPelna, skladnikiKrwi=skladnikiKrwi, krwinkiCzerwone=krwinkiCzerwone)
### endPIELEGNIARKA ###

### ADMIN ###
@app.route('/admin', methods=['GET'])
def admin():
    if not session.get('login'):
        return redirect('/main')
    if session['login'][0] != 'A':
        return redirect('/panel')
    if request.method == "GET":
        placowki = getPlacowki(mysql)
        return render_template("admin.html", placowki=placowki)

@app.route('/adminDodajePlacowke', methods=["POST"])
def adminDodajePlacowke():
    if not session.get('login'):
        return redirect('/main')
    if session['login'][0] != 'A':
        return redirect('/panel')
    placowki = getPlacowki(mysql)
    nazwa = request.form['nazwa_pl']
    if czyIstniejePlacowkaONazwie(mysql, nazwa):
        komunikat = "Podana placówka jest już zarejestrowana w systemie"
        return render_template("admin.html", komunikat=komunikat, placowki=placowki)
    adres = request.form['adres_pl']
    result = dodajPlacowke(mysql, nazwa, adres)
    placowki = getPlacowki(mysql)
    if (result == "Dodano"):
        komunikat = "Poprawnie dodano placówkę " + nazwa
        return render_template("admin.html", komunikat=komunikat, placowki=placowki)
    elif (result == "Error"):
        komunikat = "Błąd podczas dodawania placówkę"
        return render_template("admin.html", komunikat=komunikat, placowki=placowki)

@app.route('/adminDodajeLekarza', methods=["POST"])
def adminDodajeLekarza():
    if not session.get('login'):
        return redirect('/main')
    if session['login'][0] != 'A':
        return redirect('/panel')
    placowki = getPlacowki(mysql)
    pesel = request.form['pesel']
    if (len(pesel) != 11 or not pesel.isdigit()):
        komunikat = "Podano nieprawidłowy numer PESEL"
        return render_template("admin.html", komunikat=komunikat, placowki=placowki)
    nr_pwzl = request.form['nr_pwzl']
    if (len(nr_pwzl) != 7 or not nr_pwzl.isdigit()):
        komunikat = "Podano nieprawidłowy numer PWZ"
        return render_template("admin.html", komunikat=komunikat, placowki=placowki)
    if czyIstniejeLekarzOPwzl(mysql, nr_pwzl):
        komunikat = "Lekarz o podanym numerze PWZ jest już zarejestrowany w systemie"
        return render_template("admin.html", komunikat=komunikat, placowki=placowki)
    imie = request.form['imie']
    drugie_imie = ""
    drugie_imie = request.form['imie2']
    nazwisko = request.form['nazwisko']
    data_urodzenia = request.form['data_ur']
    adres = request.form['adres']
    telefon = request.form['tel']
    specjalizacja = "" 
    specjalizacja = request.form['spec']
    haslo = request.form['haslo'].encode('utf-8')
    hash_haslo = bcrypt.hashpw(haslo, bcrypt.gensalt())
    email = request.form['email']
    nazwa_placowki = request.form['placowka']
    result = dodajLekarza(mysql, pesel, nr_pwzl, imie, drugie_imie, nazwisko, data_urodzenia, adres, telefon, specjalizacja, hash_haslo, email, nazwa_placowki)
    if (result == "Dodano"):
        komunikat = "Poprawnie dodano lekarza " + str(nr_pwzl)
        return render_template("admin.html", komunikat=komunikat, placowki=placowki)
    elif (result == "Error"):
        komunikat = "Błąd podczas dodawania lekarza"
        return render_template("admin.html", komunikat=komunikat, placowki=placowki)

@app.route('/adminDodajePielegniarke', methods=["POST"])
def adminDodajePielegniarke():
    if not session.get('login'):
        return redirect('/main')
    if session['login'][0] != 'A':
        return redirect('/panel')
    placowki = getPlacowki(mysql)
    pesel = request.form['pesel']
    if (len(pesel) != 11 or not pesel.isdigit()):
        komunikat = "Podano nieprawidłowy numer PESEL"
        return render_template("admin.html", komunikat=komunikat, placowki=placowki)
    nr_pwzp = request.form['nr_pwzp']
    if (len(nr_pwzp) != 7 or not nr_pwzp.isdigit()):
        komunikat = "Podano nieprawidłowy numer PWZ"
        return render_template("admin.html", komunikat=komunikat, placowki=placowki)
    if czyIstniejePielegniarkaOPwzp(mysql, nr_pwzp):
        komunikat = "Pielęgniarka o podanym numerze PWZ jest już zarejestrowana w systemie"
        return render_template("admin.html", komunikat=komunikat, placowki=placowki)
    imie = request.form['imie']
    drugie_imie = ""
    drugie_imie = request.form['imie2']
    nazwisko = request.form['nazwisko']
    data_urodzenia = request.form['data_ur']
    adres = request.form['adres']
    telefon = request.form['tel']
    haslo = request.form['haslo'].encode('utf-8')
    hash_haslo = bcrypt.hashpw(haslo, bcrypt.gensalt())
    email = request.form['email']
    nazwa_placowki = request.form['placowka']
    result = dodajPielegniarke(mysql, pesel, nr_pwzp, imie, drugie_imie, nazwisko, data_urodzenia, adres, telefon, hash_haslo, email, nazwa_placowki)
    if (result == "Dodano"):
        komunikat = "Poprawnie dodano pielęgniarkę " + str(nr_pwzp)
        return render_template("admin.html", komunikat=komunikat, placowki=placowki)
    elif (result == "Error"):
        komunikat = "Błąd podczas dodawania pielęgniarki"
        return render_template("admin.html", komunikat=komunikat, placowki=placowki)

@app.route('/adminDodajeAdmina', methods=["POST"])
def adminDodajeAdmina():
    if not session.get('login'):
        return redirect('/main')
    if session['login'][0] != 'A':
        return redirect('/panel')
    placowki = getPlacowki(mysql)
    login = request.form['login']
    if czyIstniejeAdminOLogin(mysql, login):
        komunikat = "Administrator o podanym loginie jest już zarejestrowany w systemie"
        return render_template("admin.html", komunikat=komunikat, placowki=placowki)
    haslo = request.form['haslo'].encode('utf-8')
    hash_haslo = bcrypt.hashpw(haslo, bcrypt.gensalt())
    imie = request.form['imie']
    nazwisko = request.form['nazwisko']
    result = dodajAdmina(mysql, login, hash_haslo, imie, nazwisko)
    if (result == "Dodano"):
        komunikat = "Poprawnie dodano administratora " + login
        return render_template("admin.html", komunikat=komunikat, placowki=placowki)
    elif (result == "Error"):
        komunikat = "Błąd podczas dodawania administratora"
        return render_template("admin.html", komunikat=komunikat, placowki=placowki)

@app.route('/ustawieniaAdmina', methods=['GET', 'POST'])
def ustawieniaAdmina():
    if not session.get('login'):
        return redirect('/main')
    if session['login'][0] != 'A':
        return redirect('/panel')
    if request.method == "GET":
        login = session['login']
        dane = pobierzDaneAdmina(mysql, login)
        return render_template("ustawieniaAdmina.html", dane=dane)
    else:
        login = session['login']
        imie = request.form['imie']
        nazwisko = request.form['nazwisko']
        aktualizujDaneAdmina(mysql, login, imie, nazwisko)
        haslo = request.form['haslo'].encode('utf-8')
        if len(haslo) > 0:
            hash_haslo = bcrypt.hashpw(haslo, bcrypt.gensalt())
            aktualizujHasloAdmina(mysql, login, hash_haslo)
    return redirect("/admin")
### endADMIN ###


if __name__ == "__main__":
    app.run(debug=True)
    