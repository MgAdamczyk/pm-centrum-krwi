from flask_mysqldb import MySQL, MySQLdb
from datetime import date, timedelta

### GENERAL ###
def registerDawca(mysql, pesel, imie, imie2, nazwisko, rodowe, data_ur, adres, tel, email, hash_haslo, plec, legitymacja, obywatel):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO dawcy(pesel, imie, drugie_imie, nazwisko, nazwisko_rodowe, data_urodzenia, adres, telefon, email, haslo, plec, nr_legitymacji, gr_krwi, obywatelstwo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL, %s)", (pesel, imie, imie2, nazwisko, rodowe, data_ur, adres, tel, email, hash_haslo, plec, legitymacja, obywatel,))
    mysql.connection.commit()
    cur.close()

def getHaslo(mysql, login):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT haslo, pesel FROM dawcy WHERE pesel=%s",(login,))
    user = cur.fetchone()
    cur.close()
    return user

def getHasloP(mysql, login):
    login = login[1:]
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT haslo, nr_pwzp FROM pielegniarki WHERE nr_pwzp=%s",(login,))
    user = cur.fetchone()
    cur.close()
    return user

def getHasloL(mysql, login):
    login = login[1:]
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT haslo, nr_pwzl FROM lekarze WHERE nr_pwzl=%s",(login,))
    user = cur.fetchone()
    cur.close()
    return user

def getHasloA(mysql, login):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT haslo, login FROM administratorzy WHERE login=%s",(login,))
    user = cur.fetchone()
    cur.close()
    return user
### endGENERAL ###

### DAWCA ###
def pobierzDziennikDonacji(mysql, login):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT w.id_wizyty AS id_wizyty, w.data AS data, w.id_placowki AS id_placowki, b.id_badania AS id_badania, do.godz_donacji AS godz_donacji, do.rodzaj_pobrania AS rodzaj_pobrania, do.ilosc AS ilosc, p.nazwa AS nazwa FROM dawcy d JOIN wizyta w ON (d.pesel=w.pesel) JOIN badania b ON (b.id_wizyty=w.id_wizyty) JOIN donacje do ON (do.id_badania=b.id_badania) JOIN placowki p ON (p.id_placowki=w.id_placowki) WHERE d.pesel=%s ORDER BY w.data DESC",(login,))
    dziennikRow = cur.fetchall()
    cur.close()
    return dziennikRow

def pobierzDaneLekarzaByIdWywiadu(mysql, idWywiadu):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT  l.imie AS imie, l.nazwisko AS nazwisko, l.nr_pwzl AS nr_pwzl FROM lekarze l JOIN wywiad w ON (l.id_lekarza=w.id_lekarza) WHERE w.id_wywiadu=%s",(idWywiadu,))
    daneLekarzaRow = cur.fetchone()
    cur.close()
    return daneLekarzaRow

def pobierzDanePielegniarkiByIdPielegniarki(mysql, idPielegniarki):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT  imie, nazwisko, nr_pwzp FROM pielegniarki WHERE id_pielegniarki=%s",(idPielegniarki,))
    danePielegniarkiRow = cur.fetchone()
    cur.close()
    return danePielegniarkiRow 

# obliczanie ostatniej i kolejnych możliwych donacji
def pobierzInformacjeOstatniejDonacji(mysql, login):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT w.data AS data, d.rodzaj_pobrania AS rodzaj_pobrania, d.ilosc AS ilosc FROM donacje d JOIN badania b ON (d.id_badania=b.id_badania) JOIN wizyta w ON (w.id_wizyty=b.id_wizyty) WHERE w.pesel=%s ORDER BY data DESC LIMIT 1",(login,))
    ostatniaDonacjaRow = cur.fetchone()
    cur.close()
    return ostatniaDonacjaRow 

def obliczKolejneDonacje(dataOstatnia, rodzajOstatnia):
    kolejneDonacje = dict()
    if rodzajOstatnia == "Krew pełna":
        kolejneDonacje['Krew pełna'] = dataOstatnia+timedelta(days=57)
        kolejneDonacje['Krwinki białe'] = "Decyzja lekarza"
        kolejneDonacje['Krwinki czerwone 1j.'] = dataOstatnia+timedelta(days=57)
        kolejneDonacje['Krwinki czerwone 2j.'] = dataOstatnia+timedelta(days=85)
        kolejneDonacje['Osocze'] = dataOstatnia+timedelta(days=29)
        kolejneDonacje['Płytki krwi'] = dataOstatnia+timedelta(days=57)
    elif rodzajOstatnia == "Krwinki białe":
        kolejneDonacje['Krew pełna'] = dataOstatnia+timedelta(days=29)
        kolejneDonacje['Krwinki białe'] = dataOstatnia+timedelta(days=29)
        kolejneDonacje['Krwinki czerwone 1j.'] = dataOstatnia+timedelta(days=29)
        kolejneDonacje['Krwinki czerwone 2j.'] = dataOstatnia+timedelta(days=29)
        kolejneDonacje['Osocze'] = dataOstatnia+timedelta(days=29)
        kolejneDonacje['Płytki krwi'] = dataOstatnia+timedelta(days=29)
    elif rodzajOstatnia == "Krwinki czerwone 1j.":
        kolejneDonacje['Krew pełna'] = dataOstatnia+timedelta(days=57)
        kolejneDonacje['Krwinki białe'] = "Decyzja lekarza"
        kolejneDonacje['Krwinki czerwone 1j.'] = dataOstatnia+timedelta(days=57)
        kolejneDonacje['Krwinki czerwone 2j.'] = dataOstatnia+timedelta(days=85)
        kolejneDonacje['Osocze'] = dataOstatnia+timedelta(days=29)
        kolejneDonacje['Płytki krwi'] = dataOstatnia+timedelta(days=29)
    elif rodzajOstatnia == "Krwinki czerwone 2j.":
        kolejneDonacje['Krew pełna'] = dataOstatnia+timedelta(days=169)
        kolejneDonacje['Krwinki białe'] = "Decyzja lekarza"
        kolejneDonacje['Krwinki czerwone 1j.'] = dataOstatnia+timedelta(days=169)
        kolejneDonacje['Krwinki czerwone 2j.'] = dataOstatnia+timedelta(days=169)
        kolejneDonacje['Osocze'] = dataOstatnia+timedelta(days=85)
        kolejneDonacje['Płytki krwi'] = dataOstatnia+timedelta(days=85)
    elif rodzajOstatnia == "Osocze":
        kolejneDonacje['Krew pełna'] = dataOstatnia+timedelta(days=15)
        kolejneDonacje['Krwinki białe'] = "Decyzja lekarza"
        kolejneDonacje['Krwinki czerwone 1j.'] = dataOstatnia+timedelta(days=29)
        kolejneDonacje['Krwinki czerwone 2j.'] = dataOstatnia+timedelta(days=29)
        kolejneDonacje['Osocze'] = dataOstatnia+timedelta(days=15)
        kolejneDonacje['Płytki krwi'] = dataOstatnia+timedelta(days=29)
    elif rodzajOstatnia == "Płytki krwi":
        kolejneDonacje['Krew pełna'] = dataOstatnia+timedelta(days=29)
        kolejneDonacje['Krwinki białe'] = "Decyzja lekarza"
        kolejneDonacje['Krwinki czerwone 1j.'] = dataOstatnia+timedelta(days=29)
        kolejneDonacje['Krwinki czerwone 2j.'] = dataOstatnia+timedelta(days=29)
        kolejneDonacje['Osocze'] = dataOstatnia+timedelta(days=29)
        kolejneDonacje['Płytki krwi'] = dataOstatnia+timedelta(days=29)
    else:
        pass
    return kolejneDonacje

# przeliczanie składników krwi na Krew Pełną
def pobierzDonacjeDawcy(mysql, login):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT rodzaj_pobrania, ilosc FROM donacje WHERE pesel=%s", (login,))
    donacje = cur.fetchall()
    cur.close()
    return donacje

def pobierzPlecDawcy(mysql, login):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT plec FROM dawcy WHERE pesel=%s", (login,))
    plecRow = cur.fetchone()
    cur.close()
    return plecRow['plec']

def obliczSumeKP(donacje):
    KP = 0
    for donacja in donacje:
        if donacja['rodzaj_pobrania'] == "Krew pełna":
            KP += donacja['ilosc']
        elif donacja['rodzaj_pobrania'] == "Osocze":
            if donacja['ilosc'] > 600:
                KP += 250
            else:
                KP += 200
        elif donacja['rodzaj_pobrania'] == "Płytki krwi":
            if donacja['ilosc'] > 500:
                KP += 1000
            else:
                KP += 500
        elif donacja['rodzaj_pobrania'] == "Krwinki czerwone 1j.":
            if donacja['ilosc'] > 300:
                KP += 1000
            else:
                KP += 500
        elif donacja['rodzaj_pobrania'] == "Krwinki czerwone 2j.":
            if donacja['ilosc'] > 300:
                KP += 1000
            else:
                KP += 500
        elif donacja['rodzaj_pobrania'] == "Krwinki białe":
            if donacja['ilosc'] > 150:
                KP += 2000
    return KP

def sprawdźTytul(plec, KP):
    #przeliczenie KP na litry
    KP = KP * (0.001)
    KP = float(format(KP, '0.3f'))
    tytul = ""
    if plec == "K":
        if KP < 5:
            tytul = "Honorowy Dawca Krwi"
        elif KP >= 5 and KP < 10:
            tytul = "Zasłużony Honorowy Dawca Krwi III stopnia" 
        elif KP >= 10 and KP < 15:
            tytul = "Zasłużony Honorowy Dawca Krwi II stopnia"
        elif KP >= 15 and KP < 20:
            tytul = "Zasłużony Honorowy Dawca Krwi I stopnia"
        else:
            tytul = "Honorowy Dawca Krwi - Zasłużony dla Zdrowia Narodu"
    else:
        if KP < 6:
            tytul = "Honorowy Dawca Krwi"
        elif KP >= 6 and KP < 12:
            tytul = "Zasłużony Honorowy Dawca Krwi III stopnia" 
        elif KP >= 10 and KP < 18:
            tytul = "Zasłużony Honorowy Dawca Krwi II stopnia"
        elif KP >= 18 and KP < 20:
            tytul = "Zasłużony Honorowy Dawca Krwi I stopnia"
        else:
            tytul = "Honorowy Dawca Krwi - Zasłużony dla Zdrowia Narodu"
    return tytul

def pobierzRejestracje(mysql, login):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT w.id_wizyty AS id_wizyty, w.data AS data, w.godzina AS godzina, p.nazwa AS nazwa, wy.id_wywiadu AS id_wywiadu, a.id_ankiety AS id_ankiety FROM wizyta w JOIN placowki p ON (w.id_placowki = p.id_placowki) LEFT JOIN ankieta a ON (a.id_wizyty = w.id_wizyty) LEFT JOIN wywiad wy ON (wy.id_wizyty = w.id_wizyty) WHERE w.pesel=%s ORDER BY data DESC",(login,))
    rejestracje = cur.fetchall()
    cur.close()
    return rejestracje

def usunRej(mysql, idRejestracji):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM wizyta WHERE id_wizyty=%s", (idRejestracji,))
    mysql.connection.commit()
    cur.close()
    try:
        usunAnkieteByWizyta(mysql, idRejestracji)
    except:
        pass

def usunAnkieteByWizyta(mysql, idRejestracji):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM ankieta WHERE id_wizyty=%s", (idRejestracji,))
    mysql.connection.commit()
    cur.close()

def dodajAnk(mysql, idWizyty, odpowiedzi, data):
    cur = mysql.connection.cursor()
    parametry = [int(idWizyty), data] + odpowiedzi
    parametry = tuple(parametry) 
    cur.execute("INSERT INTO ankieta (id_wizyty, data_wyp, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27, p28, p29, p30, p31, p32, p33, p34, p35) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", parametry)
    mysql.connection.commit()
    cur.close()

def usunAnk(mysql, idAnkiety):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM ankieta WHERE id_ankiety=%s", (idAnkiety,))
    mysql.connection.commit()
    cur.close()

def dodajRejestracje(mysql, pesel, data, godzina, placowka):
    cur = mysql.connection.cursor()
    id_placowki = getIdPlacowkiByNazwa(mysql, placowka)
    cur.execute("INSERT INTO wizyta(pesel, data, godzina, id_placowki) VALUES (%s, %s, %s, %s)", (pesel, data, godzina, id_placowki,))
    mysql.connection.commit()
    cur.close()

def getIdPlacowkiByNazwa(mysql, placowka):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id_placowki FROM placowki WHERE nazwa=%s",(placowka,))
    idPlacowkiRow = cur.fetchone()
    cur.close()
    return idPlacowkiRow['id_placowki']

def pobierzDaneDawcy(mysql, login):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT pesel, imie, drugie_imie, nazwisko, nazwisko_rodowe, data_urodzenia, adres, telefon, email, plec, nr_legitymacji, gr_krwi, obywatelstwo FROM dawcy WHERE pesel=%s",(login,))
    user = cur.fetchone()
    cur.close()
    return user

def aktualizujDane(mysql, login, imie, imie2, nazwisko, rodowe, plec, data_ur, obywatel, adres, tel, email, legitymacja):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("UPDATE dawcy SET imie=%s, drugie_imie=%s, nazwisko=%s, nazwisko_rodowe=%s, data_urodzenia=%s, adres=%s, telefon=%s, email=%s, plec=%s, nr_legitymacji=%s, obywatelstwo=%s WHERE pesel=%s", (imie, imie2, nazwisko, rodowe, data_ur, adres, tel, email, plec, legitymacja, obywatel, login))
    mysql.connection.commit()
    cur.close()

def aktualizujHaslo(mysql, login, hash_haslo):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("UPDATE dawcy SET haslo=%s WHERE pesel=%s", (hash_haslo, login))
    mysql.connection.commit()
    cur.close()
### endDAWCA ###

### LEKARZ ###
def pobierzMiejscePracy(mysql, login):
    nr_pwzl = login[1:]
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id_placowki FROM lekarze WHERE nr_pwzl=%s", (nr_pwzl,))
    miejscePracyRow = cur.fetchone()
    cur.close()
    return miejscePracyRow['id_placowki']

def getNazwePlacowkiById(mysql, id_placowki):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT nazwa FROM placowki WHERE id_placowki=%s",(id_placowki,))
    PlacowkaRow = cur.fetchone()
    cur.close()
    return PlacowkaRow['nazwa']

def pobierzRejestracjeDlaLekarza(mysql, idPlacowki, data):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT d.imie AS imie, d.nazwisko AS nazwisko, w.id_wizyty AS id_wizyty, w.pesel AS pesel, w.data AS data, w.godzina AS godzina, l.id_placowki AS id_placowki, wy.id_wywiadu AS id_wywiadu, a.id_ankiety AS id_ankiety, b.id_badania AS id_badania FROM wizyta w JOIN lekarze l ON (w.id_placowki = l.id_placowki) JOIN dawcy d ON (w.pesel = d.pesel) LEFT JOIN wywiad wy ON (wy.id_wizyty = w.id_wizyty) JOIN ankieta a ON (w.id_wizyty = a.id_wizyty) LEFT JOIN badania b ON (w.id_wizyty = b.id_wizyty) WHERE l.id_placowki=%s AND data=%s ORDER BY nazwisko", (idPlacowki, data))
    rejestracje = cur.fetchall()
    cur.close()
    return rejestracje

def pobierzDaneLekarza(mysql, login):
    login = login[1:]
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT pesel, nr_pwzl, imie, drugie_imie, nazwisko, data_urodzenia, adres, telefon, specjalizacja, email FROM lekarze WHERE nr_pwzl=%s",(login,))
    lekarz = cur.fetchone()
    cur.close()
    return lekarz

def aktualizujDaneLekarza(mysql, login, imie, imie2, nazwisko, data_ur, adres, tel, email, specjalizacja):
    login = login[1:]
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("UPDATE lekarze SET imie=%s, drugie_imie=%s, nazwisko=%s, data_urodzenia=%s, adres=%s, telefon=%s, specjalizacja=%s, email=%s WHERE nr_pwzl=%s", (imie, imie2, nazwisko, data_ur, adres, tel, specjalizacja, email, login))
    mysql.connection.commit()
    cur.close()

def aktualizujHasloLekarza(mysql, login, hash_haslo):
    login = login[1:]
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("UPDATE lekarze SET haslo=%s WHERE nr_pwzl=%s", (hash_haslo, login))
    mysql.connection.commit()
    cur.close()

def pobierzAnkieteDawcy(mysql, idAnkiety):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM ankieta WHERE id_ankiety=%s",(idAnkiety,))
    ankieta = cur.fetchone()
    cur.close()
    return ankieta

def pobierzPeselByIdAnkiety(mysql, idAnkiety):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT w.pesel FROM wizyta w JOIN ankieta a ON (a.id_wizyty = w.id_wizyty) WHERE id_ankiety=%s",(idAnkiety,))
    pesel = cur.fetchone()
    cur.close()
    return pesel['pesel']

def pobierzHemoglobine(mysql, idWizyty):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT b.hb AS hb FROM wizyta w JOIN badania b ON (w.id_wizyty = b.id_wizyty) WHERE w.id_wizyty=%s",(idWizyty,))
    hb = cur.fetchone()
    cur.close()
    return hb['hb']

def dodajWywiad(mysql, login, idWizyty, wzrost, waga, temperatura, cisnienie, tetno, wezly_chlonne, skora, uwagi, akceptacja):
    login = login[1:]
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_lekarza FROM lekarze WHERE nr_pwzl=%s", (login,))
    idLekarzaRow = cur.fetchone()
    id_lekarza = idLekarzaRow['id_lekarza']
    cur.execute("INSERT INTO wywiad(id_lekarza, id_wizyty, wzrost, waga, temperatura, cisnienie, tetno, wezly_chlonne, skora, uwagi, akceptacja) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id_lekarza, idWizyty, wzrost, waga, temperatura, cisnienie, tetno, wezly_chlonne, skora, uwagi, akceptacja,))
    mysql.connection.commit()
    cur.close()

def pobierzWywiad(mysql, idWywiadu):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM wywiad WHERE id_wywiadu=%s", (idWywiadu,))
    wywiad = cur.fetchone()
    cur.close()
    return wywiad

def aktualizujWywiad(mysql, idWywiadu, wzrost, waga, temperatura, cisnienie, tetno, wezly_chlonne, skora, uwagi, akceptacja):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("UPDATE wywiad SET wzrost=%s, waga=%s, temperatura=%s, cisnienie=%s, tetno=%s, wezly_chlonne=%s, skora=%s, uwagi=%s, akceptacja=%s WHERE id_wywiadu=%s", (wzrost, waga, temperatura, cisnienie, tetno, wezly_chlonne, skora, uwagi, akceptacja, idWywiadu,))
    mysql.connection.commit()
    cur.close()
### endLEKARZ ###

### PIELEGNIARKA ###
def pobierzMiejscePracyPielegniarki(mysql, login):
    nr_pwzp = login[1:]
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id_placowki FROM pielegniarki WHERE nr_pwzp=%s", (nr_pwzp,))
    miejscePracyRow = cur.fetchone()
    cur.close()
    return miejscePracyRow['id_placowki']

def dodajRejestracjeByPielegniarka(mysql, pesel, data, godzina, id_placowki):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO wizyta(pesel, data, godzina, id_placowki) VALUES (%s, %s, %s, %s)", (pesel, data, godzina, id_placowki,))
    mysql.connection.commit()
    cur.close()

def pobierzDanePielegniarki(mysql, login):
    login = login[1:]
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT pesel, nr_pwzp, imie, drugie_imie, nazwisko, data_urodzenia, adres, telefon, email FROM pielegniarki WHERE nr_pwzp=%s",(login,))
    pielegniarka = cur.fetchone()
    cur.close()
    return pielegniarka

def aktualizujDanePielegniarki(mysql, login, imie, imie2, nazwisko, data_ur, adres, tel, email):
    login = login[1:]
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("UPDATE pielegniarki SET imie=%s, drugie_imie=%s, nazwisko=%s, data_urodzenia=%s, adres=%s, telefon=%s, email=%s WHERE nr_pwzp=%s", (imie, imie2, nazwisko, data_ur, adres, tel, email, login))
    mysql.connection.commit()
    cur.close()

def aktualizujHasloPielegniarki(mysql, login, hash_haslo):
    login = login[1:]
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("UPDATE pielegniarki SET haslo=%s WHERE nr_pwzp=%s", (hash_haslo, login))
    mysql.connection.commit()
    cur.close()

def pobierzRejestracjeByData(mysql, placowka, data):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT d.imie AS imie, d.nazwisko AS nazwisko, w.id_wizyty AS id_wizyty, w.pesel AS pesel, w.data AS data, w.godzina AS godzina, p.id_placowki AS id_placowki, wy.id_wywiadu AS id_wywiadu, wy.akceptacja AS akceptacja, a.id_ankiety AS id_ankiety, b.id_badania AS id_badania, do.id_donacji AS id_donacji FROM wizyta w JOIN pielegniarki p ON (w.id_placowki = p.id_placowki) JOIN dawcy d ON (w.pesel = d.pesel) LEFT JOIN wywiad wy ON (w.id_wizyty = wy.id_wizyty) LEFT JOIN ankieta a ON (w.id_wizyty = a.id_wizyty) LEFT JOIN badania b ON (w.id_wizyty = b.id_wizyty) LEFT JOIN donacje do ON (b.id_badania = do.id_badania) WHERE p.id_placowki=%s AND w.data=%s ORDER BY nazwisko", (placowka, data))
    rejestracje = cur.fetchall()
    cur.close()
    return rejestracje

def pobierzRejestracjeByPesel(mysql, placowka, pesel):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT d.imie AS imie, d.nazwisko AS nazwisko, w.id_wizyty AS id_wizyty, w.pesel AS pesel, w.data AS data, w.godzina AS godzina, p.id_placowki AS id_placowki, wy.id_wywiadu AS id_wywiadu, wy.akceptacja AS akceptacja, a.id_ankiety AS id_ankiety, b.id_badania AS id_badania, do.id_donacji AS id_donacji FROM wizyta w JOIN pielegniarki p ON (w.id_placowki = p.id_placowki) JOIN dawcy d ON (w.pesel = d.pesel) LEFT JOIN wywiad wy ON (w.id_wizyty = wy.id_wizyty) LEFT JOIN ankieta a ON (w.id_wizyty = a.id_wizyty) LEFT JOIN badania b ON (w.id_wizyty = b.id_wizyty) LEFT JOIN donacje do ON (b.id_badania = do.id_badania) WHERE p.id_placowki=%s AND w.pesel=%s ORDER BY w.data DESC", (placowka, pesel))
    rejestracje = cur.fetchall()
    cur.close()
    return rejestracje

def usunRejPielegniarki(mysql, idWizyty):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM wizyta WHERE id_wizyty=%s", (idWizyty,))
    mysql.connection.commit()
    cur.close()
    try:
        usunAnkieteByWizyta(mysql, idWizyty)
    except:
        pass

def pobierzIdWywiaduByIdWizyty(mysql, idWizyty):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_wywiadu FROM wywiad WHERE id_wizyty=%s", (idWizyty,))
    idWywiaduRow = cur.fetchone()
    cur.close()
    return idWywiaduRow
     
def pobierzGrupeKrwiByIdWizyty(mysql, idWizyty):
    cur = mysql.connection.cursor()
    cur.execute("SELECT d.gr_krwi FROM wizyta w JOIN dawcy d ON (w.pesel = d.pesel) WHERE w.id_wizyty=%s", (idWizyty,))
    grKrwiRow = cur.fetchone()
    cur.close()
    return grKrwiRow

def pobierzGrupyKrwi(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT grupa_krwi FROM grupy_krwi")
    grupyKrwi = cur.fetchall()
    cur.close()
    return grupyKrwi

def pobierzPeselByIdWizyty(mysql, idWizyty):
    cur = mysql.connection.cursor()
    cur.execute("SELECT pesel FROM wizyta WHERE id_wizyty=%s", (idWizyty,))
    peselRow = cur.fetchone()
    cur.close()
    return peselRow['pesel']

def dodajGrupeKrwiByIdWizyty(mysql, idWizyty, grKrwi):
    pesel = pobierzPeselByIdWizyty(mysql, idWizyty)
    cur = mysql.connection.cursor()
    cur.execute("UPDATE dawcy SET gr_krwi=%s WHERE pesel=%s", (grKrwi, pesel,))
    mysql.connection.commit()
    cur.close()

def pobierzIdBadaniaByIdWizyty(mysql, idWizyty):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_badania FROM badania WHERE id_wizyty=%s", (idWizyty,))
    idBadaniaRow = cur.fetchone()
    cur.close()
    return idBadaniaRow

def pobierzIdPielegniarki(mysql, login):
    login = login[1:]
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_pielegniarki FROM pielegniarki WHERE nr_pwzp=%s", (login,))
    idPielegniarkiRow = cur.fetchone()
    cur.close()
    return idPielegniarkiRow['id_pielegniarki']


def dodajHemoglobine(mysql, idWizyty, idPielegniarki, hb):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO badania (id_wizyty, id_pielegniarki, hb) VALUES(%s, %s, %s)", (idWizyty, idPielegniarki, hb,))
    mysql.connection.commit()
    cur.close()

def aktualizujHemoglobine(mysql, idWizyty, hb):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE badania SET hb=%s WHERE id_wizyty=%s", (hb, idWizyty,))
    mysql.connection.commit()
    cur.close()

def pobierzWynikiBadanByIdBadania(mysql, idBadania):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM morfologia m RIGHT JOIN badania b ON (b.id_badania = m.id_badania) LEFT JOIN wirusologia w ON (b.id_badania = w.id_badania) WHERE b.id_badania=%s", (idBadania,))
    wynikiRow = cur.fetchone()
    cur.close()
    return wynikiRow

def pobierzAkceptacjaWywiadByIdWizyty(mysql, idWizyty):
    cur = mysql.connection.cursor()
    cur.execute("SELECT akceptacja FROM wywiad WHERE id_wizyty=%s", (idWizyty,))
    akceptacjaRow = cur.fetchone()
    cur.close()
    return akceptacjaRow['akceptacja']

def pobierzGrupeKrwiFromDawcaByIdWizyty(mysql, idWizyty):
    cur = mysql.connection.cursor()
    cur.execute("SELECT d.gr_krwi FROM dawcy d JOIN wizyta w ON (d.pesel = w.pesel) WHERE w.id_wizyty=%s", (idWizyty,))
    grupaKrwiRow = cur.fetchone()
    cur.close()
    return grupaKrwiRow

def pobierzIdMorfologiByIdBadania(mysql, idBadania):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_morfologii FROM morfologia WHERE id_badania=%s", (idBadania,))
    morfologiaRow = cur.fetchone()
    cur.close()
    return morfologiaRow

def aktualizujMorfologie(mysql, idMorfologii, p):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE morfologia SET ht = %s, rbc = %s, wbc = %s, plt = %s, mch = %s, mchc = %s, mcv = %s, ne = %s, eo = %s, ba = %s, ly = %s, mo = %s, alat = %s WHERE id_morfologii=%s", (p['ht'], p['rbc'], p['wbc'], p['plt'], p['mch'], p['mchc'], p['mcv'], p['ne'], p['eo'], p['ba'], p['ly'], p['mo'], p['alat'], idMorfologii,))
    mysql.connection.commit()
    cur.close()

def dodajMorfologie(mysql, idBadania, p):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO morfologia (id_badania, ht, rbc, wbc, plt, mch, mchc, mcv, ne, eo, ba, ly, mo, alat) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (idBadania, p['ht'], p['rbc'], p['wbc'], p['plt'], p['mch'], p['mchc'], p['mcv'], p['ne'], p['eo'], p['ba'], p['ly'], p['mo'], p['alat'],))
    mysql.connection.commit()
    cur.close()

def pobierzIdWirusologiByIdBadania(mysql, idBadania):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_wirusologii FROM wirusologia WHERE id_badania=%s", (idBadania,))
    wirusologiaRow = cur.fetchone()
    cur.close()
    return wirusologiaRow

def aktualizujWirusologie(mysql, idWirusologii, hbs, hiv, hcv, rna_hcv, rna_hiv, dna_hbv, kila):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE wirusologia SET hbs = %s, hiv = %s, hcv = %s, rna_hcv = %s, rna_hiv = %s, dna_hbv = %s, kila = %s WHERE id_wirusologii=%s", (hbs, hiv, hcv, rna_hcv, rna_hiv, dna_hbv, kila, idWirusologii,))
    mysql.connection.commit()
    cur.close()

def dodajWirusologie(mysql, idBadania, hbs, hiv, hcv, rna_hcv, rna_hiv, dna_hbv, kila):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO wirusologia (id_badania, hbs, hiv, hcv, rna_hcv, rna_hiv, dna_hbv, kila) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (idBadania, hbs, hiv, hcv, rna_hcv, rna_hiv, dna_hbv, kila,))
    mysql.connection.commit()
    cur.close()

def pobierzRodzajePobran(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM rodzaje_pobran")
    rodzaje_pobran = cur.fetchall()
    cur.close()
    return rodzaje_pobran

def dodajDonacje(mysql, idBadania, pesel, godz, rodzaj_pobrania, ilosc):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO donacje (id_badania, pesel, godz_donacji, rodzaj_pobrania, ilosc, dostepnosc) VALUES (%s,%s,%s,%s,%s, %s)", (idBadania, pesel, godz, rodzaj_pobrania, ilosc, "TAK",))
    mysql.connection.commit()
    cur.close()

def pobierzDonacje(mysql, idWizyty):
    cur = mysql.connection.cursor()
    cur.execute("SELECT d.id_donacji, d.pesel, d.godz_donacji, d.rodzaj_pobrania, d.ilosc, d.dostepnosc FROM donacje d JOIN badania b ON (d.id_badania = b.id_badania) JOIN wizyta w ON (b.id_wizyty = w.id_wizyty) WHERE w.id_wizyty=%s", (idWizyty,))
    donacjaRow = cur.fetchone()
    cur.close()
    return donacjaRow

def aktualizujDonacje(mysql, idWizyty):
    cur = mysql.connection.cursor()
    cur.execute("SELECT d.id_donacji AS id_donacji FROM donacje d JOIN badania b ON (d.id_badania = b.id_badania) JOIN wizyta w ON (b.id_wizyty = w.id_wizyty) WHERE w.id_wizyty=%s", (idWizyty,))
    idDonacjiRow = cur.fetchone()
    idDonacji = idDonacjiRow['id_donacji']
    cur.execute("UPDATE donacje SET dostepnosc=%s WHERE id_donacji=%s", ("NIE", idDonacji,))
    mysql.connection.commit()
    cur.close()

def pobierzIloscKrwiPelnejByGrupy(mysql, idPlacowki):
    cur = mysql.connection.cursor()
    rodzaj = "Krew pełna"
    cur.execute("SELECT do.rodzaj_pobrania AS rodzaj_pobrania, da.gr_krwi AS gr_krwi, sum(do.ilosc) AS ilosc FROM donacje do JOIN badania b ON (b.id_badania = do.id_badania) JOIN wizyta w ON (b.id_wizyty=w.id_wizyty) JOIN dawcy da ON (da.pesel=w.pesel) WHERE do.rodzaj_pobrania = %s AND w.id_placowki = %s AND do.dostepnosc = %s GROUP BY gr_krwi", (rodzaj, idPlacowki,"TAK",))
    krewPelna = dict()
    for row in cur:
        krewPelna[row['gr_krwi']]=int(row['ilosc'])
    cur.close()
    return krewPelna

def pobierzIloscSkladnikowKrwiByRodzaj(mysql, idPlacowki):
    cur = mysql.connection.cursor()
    rodzaj = "Krew pełna"
    cur.execute("SELECT d.rodzaj_pobrania AS rodzaj_pobrania, SUM(d.ilosc) AS ilosc FROM donacje d JOIN badania b ON (b.id_badania=d.id_badania) JOIN wizyta w ON (w.id_wizyty=b.id_wizyty) WHERE w.id_placowki=%s AND d.rodzaj_pobrania!=%s AND d.dostepnosc = %s GROUP BY d.rodzaj_pobrania", (idPlacowki, rodzaj, "TAK",))
    skladnikiKrwi = dict()
    for row in cur:
        skladnikiKrwi[row['rodzaj_pobrania']]=int(row['ilosc'])
    cur.close()
    return skladnikiKrwi
### endPIELEGNIARKA ###

### ADMIN ###
def getPlacowki(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT nazwa, adres FROM placowki")
    rows = cur.fetchall()
    if int(cur.rowcount) == 0:
        result = []
    else:
        result = rows
    cur.close()
    return result

def dodajPlacowke(mysql, nazwa, adres):
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("INSERT INTO placowki(nazwa, adres) VALUES (%s, %s)",(nazwa,adres,))
        mysql.connection.commit()
        cur.close()
        return "Dodano"
    except:
        return "Error"

def dodajLekarza(mysql, pesel, nr_pwzl, imie, drugie_imie, nazwisko, data_urodzenia, adres, telefon, specjalizacja, hash_haslo, email, nazwa_placowki):
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT id_placowki FROM placowki WHERE nazwa=%s", (nazwa_placowki,))
        result = cur.fetchone()
        cur.execute("INSERT INTO lekarze(pesel, nr_pwzl, imie, drugie_imie, nazwisko, data_urodzenia, adres, telefon, specjalizacja, haslo, email, id_placowki) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(pesel, nr_pwzl, imie, drugie_imie, nazwisko, data_urodzenia, adres, telefon, specjalizacja, hash_haslo, email, result['id_placowki'],))
        mysql.connection.commit()
        cur.close()
        return "Dodano"
    except:
        return "Error"

def dodajPielegniarke(mysql, pesel, nr_pwzp, imie, drugie_imie, nazwisko, data_urodzenia, adres, telefon, hash_haslo, email, nazwa_placowki):
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT id_placowki FROM placowki WHERE nazwa=%s", (nazwa_placowki,))
        result = cur.fetchone()
        cur.execute("INSERT INTO pielegniarki(pesel, nr_pwzp, imie, drugie_imie, nazwisko, data_urodzenia, adres, telefon, haslo, email, id_placowki) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(pesel, nr_pwzp, imie, drugie_imie, nazwisko, data_urodzenia, adres, telefon, hash_haslo, email, result['id_placowki'],))
        mysql.connection.commit()
        cur.close()
        return "Dodano"
    except:
        return "Error"

def dodajAdmina(mysql, login, hash_haslo, imie, nazwisko):
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("INSERT INTO administratorzy(login, haslo, imie, nazwisko) VALUES (%s, %s, %s, %s)",(login, hash_haslo, imie, nazwisko,))
        mysql.connection.commit()
        cur.close()
        return "Dodano"
    except:
        return "Error"

def czyIstniejePlacowkaONazwie(mysql, nazwa):
    cur = mysql.connection.cursor()
    cur.execute("SELECT count(*) AS liczbaPlacowekONazwie FROM placowki WHERE nazwa = %s", (nazwa,))
    row = cur.fetchone()
    liczbaPlacowekONazwie = row['liczbaPlacowekONazwie']
    if int(liczbaPlacowekONazwie) == 0:
        return False
    else:
        return True

def czyIstniejeLekarzOPwzl(mysql, nr_pwzl):
    cur = mysql.connection.cursor()
    cur.execute("SELECT count(*) AS liczbaLekarzyOPwzl FROM lekarze WHERE nr_pwzl = %s", (nr_pwzl,))
    row = cur.fetchone()
    liczbaLekarzyOPwzl = row['liczbaLekarzyOPwzl']
    if int(liczbaLekarzyOPwzl) == 0:
        return False
    else:
        return True

def czyIstniejePielegniarkaOPwzp(mysql, nr_pwzp):
    cur = mysql.connection.cursor()
    cur.execute("SELECT count(*) AS liczbaPielegniarekOPwzp FROM pielegniarki WHERE nr_pwzp = %s", (nr_pwzp,))
    row = cur.fetchone()
    liczbaPielegniarekOPwzp = row['liczbaPielegniarekOPwzp']
    if int(liczbaPielegniarekOPwzp) == 0:
        return False
    else:
        return True

def czyIstniejeAdminOLogin(mysql, login):
    cur = mysql.connection.cursor()
    cur.execute("SELECT count(*) AS liczbaAdminowOLogin FROM administratorzy WHERE login = %s", (login,))
    row = cur.fetchone()
    liczbaAdminowOLogin = row['liczbaAdminowOLogin']
    if int(liczbaAdminowOLogin) == 0:
        return False
    else:
        return True

def pobierzDaneAdmina(mysql, login):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT login, imie, nazwisko FROM administratorzy WHERE login=%s",(login,))
    daneRow = cur.fetchone()
    cur.close()
    return daneRow

def aktualizujDaneAdmina(mysql, login, imie, nazwisko):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("UPDATE administratorzy SET imie=%s, nazwisko=%s WHERE login=%s", (imie, nazwisko, login,))
    mysql.connection.commit()
    cur.close()

def aktualizujHasloAdmina(mysql, login, hash_haslo):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("UPDATE administratorzy SET haslo=%s WHERE login=%s", (hash_haslo, login,))
    mysql.connection.commit()
    cur.close()
### endADMIN ###




