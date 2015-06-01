#!/usr/bin/env python

import time
import re
import json

from google.appengine.api import urlfetch


from flask import Flask, jsonify, session
from flask import request
app = Flask(__name__)

from config import config
app.secret_key = config['app']['secret_key']


from app import User
from app import Call
from app import Caller


import pages

def asPosixTime(d):
    return int(time.mktime(d.timetuple()) * 1000)

def userAsData(u):
    return {
        "id" : u.key.id(),
        "code" : u.code,
        "nickname" : u.nickname,
        "number" : u.number,
        "numberSent" : u.hasPendingContacts(),
        "social_network" : u.social_network
        }

def failureAsData(reason):
    return  {
        "result" : "failure",
        "reason" : reason
    }

def successAsData(obj):
    return  {
        "result" : "success",
        "data" : obj
    }

def resultAsData(result, process=lambda d:d):
    return failureAsData(result) if type(result) == str else successAsData(process(result))

@app.route('/call', methods=["POST"])
def call():
    number = request.form['From']
    text = request.form['Body']

    rv = Call.callReceived(number,
                           text)
    return jsonify({
        "result" : "success"
    } if isinstance(rv, Call) else failureAsData(rv))


def currentUser():
    if 'id' in session:
        return User.find(session['id'])


def extractForm(result, form, field, process=lambda a: a):
    if field in form:
        result[field] = process(form.get(field))

nameRE = re.compile("[^-a-z0-9.!&* ]", re.I)

def legalName(name):
   return nameRE.sub('', name)

def makeCall(call):
   return {
       "id" : call.key.id(),
       "caller" : call.caller.id(),
       "message" : call.message,
       "ctype" : call.ctype,
       "when" : asPosixTime(call.when),
       "thanked" : call.thanked and call.thanked.id(),
       "reported" : not not call.reported
       }

def makeCaller(caller):
    return {
        "id" : caller.key.id(),
        "nickname" : caller.nickname,
        "blocked" : caller.blocked
        }
    
@app.route('/call/<idn>/<command>', methods=["POST"])
def callPost(idn, command):
    u = currentUser()
    call = Call.find(idn)
    value = request.form.get('value', '')
    if not call or call.user != u.key:
        response = failureAsData("call not found")
    elif command == "thanked":
        response = resultAsData(call.thank(value), makeCall)
    elif command == "reported" and value:
        response = resultAsData(call.report(value))
    else:
        response = failureAsData("bad command")
    return jsonify(response)


def callerUpdate(form):
    result = {}
    extractForm(result, form, 'nickname', legalName)
    return result

@app.route('/caller/<idn>', defaults={"command":""}, methods=["POST"])
@app.route('/caller/<idn>/<command>', methods=["POST"])
def callerPost(idn, command):
    u = currentUser()
    caller = Caller.find(idn)
    value = request.form.get('value', '')
    if not caller or caller.user != u.key:
        response = failureAsData("caller not found")
    elif command == "":
        response = successAsData(caller.update(callerUpdate(request.form)))
    else:
        response = failureAsData("bad command")
    return jsonify(response)


def userIdMatches(u, idn):
    return u and ( str(u.key.id()) == str(idn) )

@app.route('/user/<idn>/<collection>', methods=["GET"])
def userGet(idn, collection):
    u = currentUser()
    if not userIdMatches(u, idn):
        response = failureAsData("bad command")
    elif collection == "callers":
        response = successAsData(map(makeCaller, u.fetchCallers()))
    elif collection == "calls":
        calls = u.fetchCalls()
        calls.sort(key=lambda call: call.when, reverse=True)
        response = successAsData(map(makeCall, calls))
    else:
         response = failureAsData("bad command")
    return json.dumps(response)

def userUpdate(form):
    result = {}
    extractForm(result, form, 'nickname', legalName)
    return result


@app.route('/user/<idn>', defaults={"command":""}, methods=["POST"])
@app.route('/user/<idn>/<command>', methods=["POST"])
def userPost(idn, command):
    u = User.find(idn)
    if command == "sendNumber":
        contact = u.sendNumber(request.form['number'])
        rv = successAsData({})
    elif command == "confirm":
        confirmed = u.confirmCode(request.form['code'])
        rv = successAsData({
            "number" : confirmed.number
        }) if confirmed else failureAsData("code not recognized")
    elif command == "":
        rv = successAsData(u.update(userUpdate(request.form)))
    else:
        rv = failureAsData("command not recognized")

    return jsonify(rv) 


def facebookValidate(access_token):
    result = urlfetch.fetch(url="https://graph.facebook.com/me?access_token=" + access_token)
    if result.status_code == 200:
        validation = json.loads(result.content)
        if validation["verified"]:
            return validation

def googleValidate(access_token):
    result = urlfetch.fetch(url="https://www.googleapis.com/plus/v1/people/me?access_token=" + access_token)
    print "CODE: ",result.status_code
    if result.status_code == 200:
        validation = json.loads(result.content)
        print validation
        return {
            "id" : validation['id'],
            "first_name" : validation['name']['givenName']
            }
    

@app.route('/user/signin', methods=["POST"])
def userSignin():
    network = request.form.get('network')
    access_token = request.form.get('access_token')
    u = None
    if network == 'facebook':
        u = facebookValidate(access_token)
    elif network == 'google':
        u = googleValidate(access_token)
    else:
        reason = 'bad network'
        
    if u:
        u = (User.findBySocialID(network, u["id"]) or
             User.register(network, u["id"], u["first_name"]))
        session['id'] = u.key.id()
    else:
        reason = 'invalid user'
        
    return jsonify(successAsData(userAsData(u))
                   if u else 
                   failureAsData(reason) )

@app.route('/user/signout', methods=["POST"])
def userSignout():
    session.pop('id', None)
    return jsonify(successAsData({}))


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500


@app.route('/')
def index():
    return pages.renderIndex(config)

@app.route('/placard/<code>')
def placard(code):
    return pages.renderPlacard(config, code)

@app.route('/redirect')
def redirect():
    return pages.renderRedirect(config)
