# Dummy Key Finder — Flask Web App

## Project files
- `app.py` — Flask backend and API routes
- `templates/index.html` — browser interface
- `requirements.txt` — Python packages

## Run on your computer
1. Install Python.
2. Open a terminal in this folder.
3. Install packages: `pip install -r requirements.txt`
4. Start the app: `python app.py`
5. Open `http://127.0.0.1:5000` in your browser.

## API endpoints
- `GET /api/status` — reads simulated device status
- `POST /api/pair` — toggles paired / unpaired state
- `POST /api/find` — starts the simulated alarm (requires pairing)
- `POST /api/stop` — stops the simulated alarm

## Deploy free on Render
1. Upload these files to a GitHub repository.
2. In Render, choose **New → Web Service** and connect the repository.
3. Set **Build Command** to `pip install -r requirements.txt`.
4. Set **Start Command** to `gunicorn app:app`.
5. Select the **Free** instance and deploy.

Free Render services can sleep after 15 minutes without incoming traffic, so the first visit after inactivity may take around a minute to load. This is a demo simulation; it does not connect to physical Bluetooth hardware.
