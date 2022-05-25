# monitor-control.py

Schaltet per Taster den Monitor in der Fahrzeughalle an oder aus.

## Skript als Service auf Raspbian ausführen

### Voraussetzungen

- Der Fernseher muss immer vor der Stromversorgung an den Raspberry Pi angeschlossen werden.
- Alle HDMI-CEC-Steueroptionen müssen am Fernseher aktiviert sein.
- In den Sperr-Optionen des Fernsehers sollten über den Hotel-Modus alle Eingangsquellen, außer der Monitor, gesperrt werden (Standard Passwort zum entsperren: `0000`).  
  (Das ist wichtig, um zu gewährleisten, dass nach einem Neustart aller Systeme die richtige Quelle im Fernseher gewählt ist.)

### Installation

#### 1. Python Modul `cec` mit Abhängigkeiten installieren:

       sudo apt install python3-dev build-essential libcec-dev cec-utils && pip3 install cec

#### 2. `monitor-control.py` nach `/usr/bin` kopieren.
#### 3. Service erstellen:

       sudo nano /lib/systemd/system/monitor-control.service
   
   Inhalt von `monitor-control.service`:

       [Unit]
       Description=Monitor Control

       [Service]
       Type=simple
       ExecStart=/usr/bin/python3 /usr/bin/monitor-control.py
       User=pi

       [Install]
       WantedBy=multi-user.target

#### 4. Systemctl Daemon aktualisieren:

       sudo systemctl daemon-reload

#### 5. Service aktivieren:

       sudo systemctl enable monitor-control

#### 6. Service starten:

       sudo systemctl start monitor-control

#### 7. HDMI Hotplug aktivieren:  
   Dazu folgende Zeile in `/boot/config.txt` ***ent***kommentieren:

       hdmi_force_hotplug=1

## Basis Befehle von CEC-Util

<table>
  <tr>
    <td>An</td>
    <td><pre>echo on 0 | cec-client -s -d 1</pre></td>
  </tr>
  <tr>
    <td>Aus</td>
    <td><pre>echo standby 0 | cec-client -s -d 1</pre></td>
  </tr>
  <tr>
    <td>Bildschirm Status</td>
    <td><pre>echo pow 0 | cec-client -s -d 1</pre></td>
  </tr>
  <tr>
    <td>Hilfe</td>
    <td><pre>echo h | cec-client -s -d 1</pre></td>
  </tr>
</table>
