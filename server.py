
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, flash, session, url_for

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config.from_mapping(SECRET_KEY='dev')

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
DATABASEURI = "postgresql://at3456:Tang0926@@34.73.36.248/project1" # Modify this with your own credentials you received from Joseph!

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
#engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

  account_id = session.get('account_id')

  if account_id is None:
      g.account = None
  else:
      g.account = g.conn.execute(text(
          'SELECT * FROM account WHERE account_id = :x'), x=account_id
      ).fetchone()

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
@app.route('/index')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)
  print('\n')

  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        account = g.conn.execute(
          text(
            'SELECT * FROM account WHERE email = :x'
          ), x=email
        ).fetchone()

        if account is None:
            error = 'Incorrect email.'
        elif account['password'] != password:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['account_id'] = account['account_id']
            return redirect('index')

        flash(error)

    return render_template('login.html')

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None

        if not email:
          error = 'Email is required.'
        elif not password:
          error = 'Password is required.'
        elif g.conn.execute(
          text(
            'SELECT email FROM account WHERE email = :x'
          ), x=email
        ).fetchone() is not None:
          error = 'Email {} is already registered.'.format(email)

        if error is None:
          max_id = g.conn.execute(
            'SELECT MAX(account_id) FROM account'
          ).fetchone()
          new_id = max_id['max'] + 1
          g.conn.execute(
            text(
              'INSERT INTO account VALUES (:x, :y, :z)'
            ), x=new_id, y=email, z=password
          )
          return redirect('login')

        flash(error)

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('index')

@app.route('/anime') 
def generate_page():
    anime_id = request.args.get('anime_id')
    anime = g.conn.execute(
        text(
            'SELECT * FROM anime WHERE anime_id = :x'
        ), x=anime_id
    ).fetchone()

    reviews = g.conn.execute(
      'SELECT *'
      ' FROM anime NATURAL JOIN describes NATURAL JOIN review NATURAL JOIN writes'
      ' WHERE anime_id = %s AND deleted = FALSE', anime_id
    ).fetchall()

    comments = g.conn.execute(
      'SELECT *'
      ' FROM anime NATURAL JOIN belongs NATURAL JOIN comment NATURAL JOIN posts'
      ' WHERE anime_id = %s', anime_id
    ).fetchall()

    write_url = "write?anime_id=" + str(anime_id)
    post_url = "post?anime_id=" + str(anime_id)
    return render_template('anime.html', anime=anime, reviews=reviews, 
      comments=comments, write_url=write_url, post_url=post_url)

@app.route('/write', methods=('GET', 'POST'))
def write():
    if request.method == 'POST':
        anime_id = request.form['anime_id']
        text = request.form['text'].strip()
        error = None

        if not text:
            error = 'Text is required.'

        if error is not None:
            flash(error)
        else:
            review_id = g.conn.execute(
              'SELECT MAX(CAST(review_id AS INTEGER)) FROM review'
            ).fetchone()
            new_id = str(review_id['max'] + 1)

            g.conn.execute(
              'INSERT INTO review VALUES(%s, %s, FALSE)', new_id, text
            )
            g.conn.execute(
              'INSERT INTO describes VALUES (%s, %s)', new_id, anime_id
            )
            g.conn.execute(
              'INSERT INTO writes VALUES (%s, %s)', g.account['account_id'], new_id
            )
            return redirect('anime?anime_id=' + str(anime_id))

    anime_id = request.args.get('anime_id')
    return render_template('write.html', anime_id=anime_id)

@app.route('/post', methods=('GET', 'POST'))
def post():
    if request.method == 'POST':
        anime_id = request.form['anime_id']
        text = request.form['text'].strip()
        episode = request.form['episode']
        error = None

        total_ep = g.conn.execute(
          'SELECT num_episodes FROM anime WHERE anime_id=%s', anime_id
        ).fetchone()['num_episodes']
        if total_ep == 'Unknown':
            error = 'Sorry, comments cannot be added to this anime.'
            flash(error)
            return render_template('post.html', anime_id=anime_id)

        if not episode:
            error = 'Episode number is required.'
        elif int(episode) > int(total_ep) or int(episode) <= 0:
            error = 'Episode does not exist.'

        if not text:
            error = 'Text is required.'

        if error is not None:
            flash(error)
        else:
            comment_id = g.conn.execute(
              'SELECT MAX(CAST(comment_id AS INTEGER)) FROM comment'
            ).fetchone()
            new_id = str(comment_id['max'] + 1)

            g.conn.execute(
              'INSERT INTO comment VALUES(%s, %s)', new_id, text
            )
            g.conn.execute(
              'INSERT INTO belongs VALUES (%s, %s, %s)', new_id, anime_id, int(episode)
            )
            g.conn.execute(
              'INSERT INTO posts VALUES (%s, %s)', g.account['account_id'], new_id
            )
            return redirect('anime?anime_id=' + str(anime_id))

    anime_id = request.args.get('anime_id')
    return render_template('post.html', anime_id=anime_id)

@app.route('/search', methods=['POST'])
def recommend_animes():
  genres = request.form['genres']
  exclude = request.form['exclude']
  minRating = request.form['min_rating']
  listGenres = genres.split()
  excludeGenres = exclude.split()
  error = None

  minNum = 0
  if minRating is None:
    minNum = float(minRating)

  if not genres:
    error = 'Please enter a genre(s).'  

  if error is not None:
    flash(error)
  else:
    g.conn.execute(text('CREATE TABLE #DesiredGenres (genre varchar(20) not null, primary key(genre))'))
    g.conn.execute(text('CREATE TABLE #BadGenres (genre varchar(20) not null, primary key(genre))'))
    for genre in listGenres:
        g.conn.execute(text('INSERT INTO #DesiredGenres :a'), a=genre)
    for badgenre in excludeGenres:
        g.conn.execute(text('INSERT INTO #BaddGenres :b'), b=badgenre)

    recommendedAnimes = g.conn.execute(text(
          ' SELECT anime_name, anime_id '
          ' FROM (SELECT anime_name, anime_id, COUNT(anime_genre) FROM anime NATURAL JOIN anime_genre '
          ' WHERE anime_genre IN #DesiredGenres AND average_rating > :y AND anime_id NOT IN (#BadGenres) '
          ' GROUP BY anime_name, anime_id '
          ' ORDER BY COUNT(anime_genre) ) '
          ' GROUP BY anime_name, anime_id '
      ), y=minNum
      ).fetchall()

    animeIDs = g.conn.execute(text(
          ' SELECT anime_id '
          ' FROM (SELECT anime_name, anime_id, COUNT(anime_genre) FROM anime NATURAL JOIN anime_genre '
          ' WHERE anime_genre IN #DesiredGenres AND average_rating > :y AND anime_id NOT IN (#BadGenres) '
          ' GROUP BY anime_name, anime_id '
          ' ORDER BY COUNT(anime_genre) ) '
          ' GROUP BY anime_name, anime_id '
      ), y=minNum
      ).fetchall()

    animeList = []
    for ID in animeIDs:
        animeUrl = 'anime?anime_id=' + str(ID)
        animeList.append(animeUrl)

    g.conn.execute(text('DROP TABLE #DesiredGenres'))
    g.conn.execute(text('DROP TABLE #BadGenres'))

    return render_template('recommendations.html', recommendedAnimes=recommendedAnimes, animeList=animeList)
  
  return redirect('index')

@app.route('/lookup', methods=['POST'])
def lookup():
  anime_in = request.form['anime_name'].strip()
  error = None

  if not anime_in:
    error = 'Please enter an anime.'
  
  if error is not None:
    flash(error, 'anime_in')
  else:
    anime = g.conn.execute(
      'SELECT * FROM anime WHERE UPPER(anime_name) LIKE UPPER(%s)', '%'+anime_in+'%'
    ).fetchall()
    
    if not anime:
      error = '\"{}\" is not an Anime!'.format(anime_in)
      flash(error, 'anime_in')
      return redirect('index')
    else:
      return render_template('/anime_list.html', animes=anime, anime_in=anime_in)
  
  return redirect('index')

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()