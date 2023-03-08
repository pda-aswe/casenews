# template 

Dieses Repo soll nur als Template dienen für alle weiteren Services und Use-Cases. Wenn ein neues Repo erstellt wird von diesem Template sollte es public sein, da sonst Github-Actions und das Erstellen der Dockerimages eingeschränkt ist.

## Allgemein
- Zur Übertragung von Dateien zwischen Services wird MQTT als Publisher/Subscribe Eventbroker verwendet. Im Main-Skript wird eine automatische Verbindung mit dem MQTT-Broker aufgebaut.
- Wenn der Main-Branch auf Github aktualisiert wird, wird automatisch ein Docker-Image daraus erstellt. Es darf jedoch kein pytest fehlschlagen.
- Wenn andere Module außer den Standardpythonmodulen verwendet werden, dann müssen diese in die requirements.txt eingefügt werden. Die Datei würd für die Erstellung des Dockerimages verwendet.
- Für die Tests gibt es den Ordner tests. Zum Testen des Pythoncode wird pytest verwendet, da es einfach in Github Action zu integrieren ist.
- Tests können lokal mit `pytest` ausgeführt werden. Das muss mit `pip3 install pytest` nachinstalliert werden.
- Damit die Tests gefunden werden, muss die Datei und der Funktionsname mit `test_` beginnen.
- Mit `pytest --func_cov=src tests/ -v` laufen alle Tests durch. Das muss mit `pip3 install pytest-func-cov` nachinstalliert werden.
- Im Dockercontainer wird immer die Datei src/main.py ausgeführt
- So kann Request/Response mit MQTT integriert werden: [Understanding And Using MQTT v5 Request Response](http://www.steves-internet-guide.com/mqttv5-request-response/)