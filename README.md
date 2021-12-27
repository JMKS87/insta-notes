### Insta-notes
Simple project based on websites like <http://wepaste.com> or <http://cl1p.net>.

### Deploy
1. Should have Docker installed.
2. Build: `docker build -t insta-notes .`
3. Run: `docker run -p 80:80 insta-notes`
4. App is running on `localhost`, port 80.

### Local development
1. Should have Python3.8+, preferably with Virtualenv.
2. `pip install -r requirements.txt` or `requirements_dev.txt` for tests to work.
3. `python app/main.py` for development server.
4. `pytest` for running tests.
