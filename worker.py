from mojek_service.app import app
import os
# https://stackoverflow.com/questions/17260338/deploying-flask-with-heroku

if __name__ == "__main__":
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)