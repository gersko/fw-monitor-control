# monitor-control.py

## Funktion

Schaltet per Taster oder HTTP Request den Monitor in der Fahrzeughalle an oder aus.

## Einrichtung: Skript als Service in Raspberry Pi OS ausführen

### Voraussetzungen

- Der Fernseher muss immer vor der Stromversorgung an den Raspberry Pi angeschlossen werden.
- Alle HDMI-CEC-Steueroptionen müssen am Fernseher aktiviert sein.
- In den Sperr-Optionen des Fernsehers sollten über den Hotel-Modus alle Eingangsquellen, außer der FF-Agent Monitor, gesperrt werden (Standard Passwort zum entsperren: `0000`).  
  (Das ist wichtig, um zu gewährleisten, dass nach einem Neustart aller Systeme die richtige Quelle im Fernseher gewählt ist.)

### Funktionierende Umgebung

- Raspberry Pi OS 10 (Buster), 12 (Bookworm) auf einem Pi Zero W
- Python 3.7, 3.10
  - [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) 0.7.1
  - [python-cec](https://github.com/trainman419/python-cec) 9ec546f (Version 0.2.8 mit Bugfix, der verhindert, dass die Funktion `cec.init()` einfriert, wenn sie fehlschlägt, siehe [#61](https://github.com/trainman419/python-cec/issues/61) und Implementierung von `cec.close()`, siehe [#64](https://github.com/trainman419/python-cec/issues/64).)

### Installation

1. **Abhängigkeiten des Python Moduls [`python-cec`](https://github.com/trainman419/python-cec) installieren:**

   ```
   sudo apt install libcec-dev build-essential python3-dev
   ```

2. **In das Verzeichnis `/home/pi` wechseln und Repository klonen:**

   ```
   cd /home/pi/
   ```
   ```
   git clone https://github.com/gersko/fw-monitor-control
   ```

3. **Virtual Environment erstellen und [`python-cec`](https://github.com/trainman419/python-cec) installieren**

   ```
   cd fw-monitor-control/
   ```
   ```
   python -m venv .venv
   ```
   ```
   .venv/bin/pip install -r requirements.txt
   ```

4. **Service erstellen:**
   ```
   sudo nano /lib/systemd/system/monitor-control.service
   ```

   Inhalt von `monitor-control.service`:

   ```   
   [Unit]
   Description=Monitor Control
   StartLimitIntervalSec=300
   StartLimitBurst=3
   StartLimitAction=reboot

   [Service]
   Type=simple
   Restart=always
   RestartSec=5s
   ExecStart=/home/pi/fw-monitor-control/.venv/bin/python /home/pi/fw-monitor-control/monitor-control.py
   User=root

   [Install]
   WantedBy=multi-user.target
   ```

5. **Service aktivieren und starten:**

   Systemctl Daemon aktualisieren:

   ```
   sudo systemctl daemon-reload
   ```

   Service aktivieren:

   ```
   sudo systemctl enable monitor-control
   ```

   Service starten:

   ```
   sudo systemctl start monitor-control
   ```

6. **HDMI Hotplug aktivieren:**  
   Dazu folgende Zeile in `/boot/firmware/config.txt` hinzufügen:

   ```
   hdmi_force_hotplug=1
   ```


## Bedienung

### Monitor per Taster steuern

Um den Monitor an-/auszuschalten zieht man, bei Verwendung eines Pi Zeros, mit dem Taster `GPIO 18` auf `GND`. Wenn ein anderes Board verwendet wird, muss evtl. der GPIO Pin im Skript angepasst werden.

### Monitor per HTTP Request steuern

Der Monitor kann ebenso über folgende HTTP Requests gesteuert werden:

#### Monitor anschalten:

       GET http://<ip-address>:8080/monitor?turn=on

#### Monitor ausschalten:

       GET http://<ip-address>:8080/monitor?turn=off

#### Monitor Status abfragen:

       GET http://<ip-address>:8080/monitor?state

## Troubleshooting Hilfe: Der `cec-client`

Der `cec-client` ist Teil von [`cec-utils`](https://github.com/Pulse-Eight/libcec), einer Library, mit der CEC-fähige Monitore/Fernseher gesteuert werden können. Er kann nur genutzt werden, wenn `monitor-control.py` nicht aktiv ist.

### Installation von [`cec-utils`](https://github.com/Pulse-Eight/libcec):

    sudo apt install cec-utils

### Eine Auswahl von wichtigen Befehlen:

| Aktion                          | Befehl                                 |
| ------------------------------- | -------------------------------------- |
| An                              | `echo on 0 \| cec-client -s -d 1`      |
| Aus                             | `echo standby 0 \| cec-client -s -d 1` |
| Bildschirm Status               | `echo pow 0 \| cec-client -s -d 1`     |
| Nach verfügbaren Geräten suchen | `echo scan \| cec-client -s -d 1`      |
| Alle Befehle anzeigen           | `echo h \| cec-client -s -d 1`         |