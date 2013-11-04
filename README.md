Mickey Dees.

https://devcenter.heroku.com/articles/getting-started-with-python

    virtualenv venv --distribute
    virtualenv venv --relocatable

    source venv/bin/activate

    pip install Flask gunicorn
    # OR
    pip install -r requirements.txt
   
    foreman start
