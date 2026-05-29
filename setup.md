# Setup Notes

## Install dependencies
pip3 install -r requirements.txt --break-system-packages
sudo apt install mosquitto mosquitto-clients sqlite3 -y
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

## Run the system (3 separate terminals)
python3 backend/app.py
python3 dashboard/app.py
python3 device/doorbell_combo.py

## Check database
sqlite3 data/doorcam.db "SELECT * FROM events ORDER BY id DESC LIMIT 10;"
