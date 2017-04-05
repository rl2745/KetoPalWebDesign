#!/usr/bin/env python2.7

#Created by Michael Sheng(ms4973) and Richard Lopez(rl2745)
#Date Created - April 5, 2017
#COMS W4111

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
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#
DATABASEURI = "postgresql://ms4973:norice@104.196.18.7/w4111"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#

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
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

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
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT pname FROM person")
  names = []
  for result in cursor:
    names.append(result['pname'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
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


@app.route('/foods', methods=['GET','POST'])
def foods():
  names = g.conn.execute("SELECT fname FROM food").fetchall()
  name = names[0][0]
  if request.method == 'POST':
    name = request.form['userDropdown']
  food = g.conn.execute(text("SELECT * FROM food WHERE fname= :nm "),nm=name).fetchone()
  context = dict(names=names, food=food)

  return render_template("foods.html", **context)

@app.route('/exercises', methods=['GET','POST'])
def exercises():
  names = g.conn.execute("SELECT ename FROM exercise").fetchall()
  name = names[0][0]
  if request.method == 'POST':
    name = request.form['userDropdown']
  exercise = g.conn.execute(text("SELECT * FROM exercise NATURAL JOIN (SELECT eid, speed, Null as sets, Null as reps, Null as weight FROM cardio_exercise UNION SELECT eid, Null as speed, sets, reps, weight FROM strength_exercise) t1 WHERE ename= :nm "),nm=name).fetchone()
  context = dict(names=names, exercise = exercise)
  return render_template("exercises.html", **context)

@app.route('/diets', methods=['GET','POST'])
def diets():
  names = g.conn.execute("SELECT dname FROM diet").fetchall()
  name = names[0][0]
  if request.method == 'POST':
    name = request.form['userDropdown']
  diet = g.conn.execute(text("SELECT fname, calories FROM diet NATURAL JOIN consists_of NATURAL JOIN food WHERE dname = :nm "),nm=name).fetchall()
  calories = g.conn.execute(text("SELECT SUM(calories) AS num FROM diet NATURAL JOIN consists_of NATURAL JOIN food GROUP BY dname HAVING dname = :nm "),nm=name).fetchone()
  context = dict(name=name, names=names, diet = diet, calories = calories)
  return render_template("diets.html", **context)

@app.route('/newDiet', methods=['GET','POST'])
def newDiet():
  foods = g.conn.execute("SELECT fname FROM food").fetchall()
  if request.method == 'POST':
    foodsToAdd = request.form.getlist('food')
    print foodsToAdd
    dname = str(request.form['name'])
    print dname
    did = g.conn.execute("SELECT MAX(did) FROM diet").fetchone()[0] + 1
    g.conn.execute(text("INSERT INTO diet VALUES ( :di , :nm )"),di=did,nm=dname)

    for food in foodsToAdd:
      fid = g.conn.execute(text("SELECT fid FROM food WHERE fname = :fn "),fn=food).fetchone()[0]
      g.conn.execute(text("INSERT INTO consists_of VALUES ( :di , :fi )"),di=did,fi=fid)

    return redirect('/diets')
  context = dict(foods=foods, newDiet = newDiet)
  return render_template("newDiet.html", **context)

@app.route('/workouts', methods=['GET','POST'])
def workouts():
  names = g.conn.execute("SELECT wname FROM workout_program").fetchall()
  name = names[0][0]
  if request.method == 'POST':
    name = request.form['userDropdown']
  workout = g.conn.execute(text("SELECT ename, cal_expend_per_lb FROM exercise NATURAL JOIN uses NATURAL JOIN workout_program WHERE wname = :nm "),nm=name).fetchall()
  tcal = g.conn.execute(text("SELECT SUM(cal_expend_per_lb) AS num FROM exercise NATURAL JOIN uses NATURAL JOIN workout_program GROUP BY wname HAVING wname = :nm "),nm=name).fetchone()
  context = dict(name=name, names=names, workout = workout, tcal=tcal)
  return render_template("workouts.html", **context)

@app.route('/newWorkout', methods=['GET','POST'])
def newWorkout():
  exercises = g.conn.execute("SELECT ename FROM exercise").fetchall()
  if request.method == 'POST':
    exercisesToAdd = request.form.getlist('exercise')
    print exercisesToAdd
    wname = str(request.form['name'])
    print wname
    wid = g.conn.execute("SELECT MAX(wid) FROM workout_program").fetchone()[0] + 1
    g.conn.execute(text("INSERT INTO workout_program VALUES ( :wi , :nm )"),wi=wid,nm=wname)

    for exercise in exercisesToAdd:
      eid = g.conn.execute(text("SELECT eid FROM exercise WHERE ename = :en "),en=exercise).fetchone()[0]
      g.conn.execute(text("INSERT INTO uses VALUES ( :wi , :ei )"),wi=wid,ei=eid)

    return redirect('/workouts')
  context = dict(exercises=exercises, newWorkout = newWorkout)
  return render_template("newWorkout.html", **context)

@app.route('/competitions', methods=['GET','POST'])
def competitions():
  comps = g.conn.execute("SELECT DISTINCT cname FROM competition").fetchall()
  comp = comps[0][0]
  if request.method == 'POST':
    comp = request.form['userDropdown']
  competition = g.conn.execute(text("SELECT * FROM ((SELECT C.cid, C.win_condition, P.email, C.cname, C.start, C.stop FROM competition C JOIN participates P ON C.cid=P.cid) T1 NATURAL JOIN person) WHERE cname= :cp "),cp=comp).fetchone()
  competitorsCursor = g.conn.execute(text("SELECT * FROM ((SELECT C.cid, C.win_condition, P.email, C.cname, C.start, C.stop FROM competition C JOIN participates P ON C.cid=P.cid) T1 NATURAL JOIN person) WHERE cname= :cp "),cp=comp).fetchall()
  context = dict(comps=comps, competition=competition, competitorsCursor=competitorsCursor)

  return render_template("competitions.html", **context)

@app.route('/userProfile', methods=['GET', 'POST'])
def userProfile():
  users = g.conn.execute("SELECT pname FROM person").fetchall()
  user = users[0][0]
  if request.method == 'POST':
    user = request.form['userDropdown']
  person = g.conn.execute(text("SELECT * FROM (((participates P JOIN competition C ON P.cid=C.cid) T1 JOIN (person P JOIN diet D ON P.did=D.did) T2 ON T1.email=T2.email) T3 LEFT OUTER JOIN workout_program W ON T3.wid=W.wid) WHERE pname= :up "),up=user).fetchone()
  context = dict(users=users, person=person)


  return render_template("userProfile.html", **context)


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


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
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
