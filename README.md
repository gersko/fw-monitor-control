# monitor-control.py

## Funktion

Schaltet per Taster den Monitor in der Fahrzeughalle an oder aus.  
Um den Monitor an-/auszuschalten zieht man, bei Verwendung eines Pi Zeros, mit dem Taster `GPIO 18` auf `GND`. Wenn ein anderes Board verwendet wird, muss evtl. der GPIO Pin im Skript angepasst werden.

## Einrichtung: Skript als Service in Raspbian ausführen

### Voraussetzungen

- Der Fernseher muss immer vor der Stromversorgung an den Raspberry Pi angeschlossen werden.
- Alle HDMI-CEC-Steueroptionen müssen am Fernseher aktiviert sein.
- In den Sperr-Optionen des Fernsehers sollten über den Hotel-Modus alle Eingangsquellen, außer der Monitor, gesperrt werden (Standard Passwort zum entsperren: `0000`).  
  (Das ist wichtig, um zu gewährleisten, dass nach einem Neustart aller Systeme die richtige Quelle im Fernseher gewählt ist.)

### Installation

1. **Python Modul [`python-cec`](https://github.com/trainman419/python-cec) mit Abhängigkeiten installieren:**

       sudo apt install libcec-dev build-essential python-dev && pip install cec

2. **`monitor-control.py` nach `/usr/bin` kopieren.**
3. **Service erstellen:**

       sudo nano /lib/systemd/system/monitor-control.service
   
   Inhalt von `monitor-control.service`:

       [Unit]
       Description=Monitor Control

       [Service]
       Type=simple
       ExecStart=/usr/bin/python /usr/bin/monitor-control.py
       User=pi

       [Install]
       WantedBy=multi-user.target

4. **Systemctl Daemon aktualisieren:**

       sudo systemctl daemon-reload

5. **Service aktivieren:**

       sudo systemctl enable monitor-control

6. **Service starten:**

       sudo systemctl start monitor-control

7. **HDMI Hotplug aktivieren:**  
   Dazu folgende Zeile in `/boot/config.txt` ***ent***kommentieren:

       hdmi_force_hotplug=1

## Troubleshooting Hilfe: Der `cec-client`

Der `cec-client` ist Teil von [`cec-utils`](https://github.com/Pulse-Eight/libcec), einer Library, mit der CEC-fähige Monitore/Fernseher gesteuert werden können.

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
