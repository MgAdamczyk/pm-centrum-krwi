# pm-centrum-krwi

Centrum Krwi to aplikacja webowa, która umożliwia gromadzenie i przetwarzanie danych pacjentów w punktach poboru krwi.

### Technologie

* język programowania Python z frameworkiem Flask
* HTML, CSS, Bootstrap 4
* silnik bazodanowy MySQL

### Uruchomienie

Aby uniknąć instalowania wszystkich bibliotek w używanym systemie operacyjnym, należy wykorzystać narzędzie virtualenv. Tworzy ono środowisko wirtualne pozwalające na zainstalowanie używanych pakietów jedynie w jego wnętrzu. W celu utworzenia wirtualnego środowiska należy w terminalu wykonać następujące komendy:
```
$ pip3 install virtualenv
$ virtualenv env
```
gdzie ‘env’ to nazwa środowiska.

Następnie aby do niego przejść, należy wykonać komendę:
```
$ source env/bin/activate
```

Aby zainstalować potrzebne biblioteki, należy wykonać komendę:
```
$ pip3 install flask bcrypt flask_mysqldb
```
Jeżeli na komputerze został zainstalowany python3, aplikacja może zostać uruchomiona lokalnie, po przejściu do folderu zawierającego plik ‘app.py’, poprzez wykonanie polecenia:
```
$ python3 app.py
```
Aplikacja będzie wtedy dostępna pod adresem: http://localhost:5000/


Aby umieścić aplikację na serwerze heroku (https://www.heroku.com/), należy mieć aktywne konto na tym serwerze oraz pliki projektowe wraz z folderem wirtualnego środowiska ‘env’ umieścić wewnątrz repozytorium Gitowym. Następnie w terminalu należy wykonać poniższe operacje.
```
(env)$ heroku login
```
Tu może zaistnieć potrzeba zalogowania się do serwisu w przeglądarce.

Następnie potrzebna jest instalacja pakietu gunicorn oraz zapisanie informacji o wymaganych pakietach w pliku requirements.txt
```
(env)$ pip3 install gunicorn
(env)$ pip3 freeze > requirements.txt
```
Kolejnym krokiem jest utworzenie pliku Procfile i wpisanie do niego linijki: "web: gunicorn app:app".
```
(env)$ touch Procfile
```
Aby w serwisie Heroku utworzyć nową (pustą) aplikację, należy wykonać komendę:
```
(env)$ heroku create app-name
```
Ostatnim krokiem będzie zapisanie wszystkich zmian w repozytorium oraz przesłanie plików na serwer, do czego służyć będą komendy:
```
(env)$ git add .
(env)$ git commit -m “Example message”
(env)$ git push heroku master
```
W terminalu zostanie wypisany link pozwalający na otworzenie aplikacji dostępnej w internecie.
