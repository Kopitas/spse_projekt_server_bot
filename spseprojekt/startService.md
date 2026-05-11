# Informator SPSE systemd service

This project includes a systemd service file named `informatorspse.service`.

## Install the service

Run these commands from the project directory:

```bash
./venv/bin/python -m pip install -r requirements.txt
sudo cp informatorspse.service /etc/systemd/system/informatorspse.service
sudo systemctl daemon-reload
sudo systemctl enable informatorspse
sudo systemctl start informatorspse
```

The service uses:

- working directory: `/home/dev/spseprojekt`
- Python: `/home/dev/spseprojekt/venv/bin/python`
- entry point: `/home/dev/spseprojekt/bot/run.py`
- optional environment file: `/home/dev/spseprojekt/.env`
- Linux user: `dev`

If the project is moved or should run as a different Linux user, edit `informatorspse.service` before copying it to `/etc/systemd/system/`.

## Common commands

Start the service:

```bash
sudo systemctl start informatorspse
```

Stop the service:

```bash
sudo systemctl stop informatorspse
```

Restart the service:

```bash
sudo systemctl restart informatorspse
```

Show current status:

```bash
sudo systemctl status informatorspse
```

Show live logs:

```bash
sudo journalctl -u informatorspse -f
```

Enable automatic start after boot:

```bash
sudo systemctl enable informatorspse
```

Disable automatic start after boot:

```bash
sudo systemctl disable informatorspse
```

## After changing the service file

If you edit `informatorspse.service`, copy it again and reload systemd:

```bash
sudo cp informatorspse.service /etc/systemd/system/informatorspse.service
sudo systemctl daemon-reload
sudo systemctl restart informatorspse
```
