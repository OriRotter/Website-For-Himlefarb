import base64
import os
import requests
from flask import Flask, render_template, make_response, render_template_string, request, redirect
import string
import random
from json2html import *

import livejson

app = Flask(__name__)


## Login methods ##
@app.route("/login", methods=["GET"])
def login():
    try:
        codeNumber = request.args.get('code')
        numberCode = base64.b64decode(codeNumber)
        numberCode = numberCode.decode("ascii")
        print(number)
        if str(numberCode) == str(number):
            return render_template("login.html")
        return render_template("404.html")
    except:
        return render_template("404.html")



@app.route("/")
def tryagain():
    return render_template("404.html")


@app.after_request
def add_header(response):
    """
    Add headers to both force the latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


############
### MAIN ###
############


## Main methods ##


number = 0
userNamesList = []
userNamesDict = livejson.File("users.json")


def getRandomString(size):
    return ''.join(random.choices(string.ascii_letters, k=size))


link = getRandomString(3)
print(f"Login is in /{link}")


@app.route(f'/{link}')
def home():
    global number
    number += 1
    if number > 50:
        number = 1
    code = base64.b64encode(str(number).encode('ascii')).decode('ascii')
    return redirect(f"/login?code={code}", code=302)


@app.route('/success', methods=["POST"])
def success():
    username = request.form['username'].replace(' ', '')
    userFamilyName = request.form['userFamilyName'].replace(' ', '')
    userId = request.form['userId'].replace(' ', '')
    name = f"{username} {userFamilyName}|{userId}"
    print(f"The name: {name}. IP: {request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)}")
    if name in userNamesList:
        return render_template("unSuccess.html")
    else:
        userNamesList.append(name)
        if name in userNamesDict:
            userNamesDict[name] += 1
        else:
            userNamesDict[name] = 1
        return render_template("success.html")


def resetAndQR():
    global userNamesList
    userNamesList = []
    try:
        # מוחק את הקישור הקודם
        headers = {
            'Authorization': 'Bearer ThXxSbSNbRaIZmuQ',
            'Content-Type': 'application/json',
        }

        params = {
            'limit': '2',
            'page': '1',
            'order': 'date',
        }

        response = requests.get('https://urlshort.in/api/urls', params=params, headers=headers).json()
        num = response["data"]["urls"][0]["id"]
        headers = {
            'Authorization': 'Bearer ThXxSbSNbRaIZmuQ',
            'Content-Type': 'application/json',
        }

        requests.delete(f'https://urlshort.in/api/url/{num}/delete', headers=headers)
    except:
        print("didn't shorten a link before")
        pass
    # יוצר קישור חדש
    headers = {
        'Authorization': 'Bearer ThXxSbSNbRaIZmuQ',
        'Content-Type': 'application/json',
    }
    json_data = {
        'url': f'https://or1.pythonanywhere.com/{link}'
    }
    response = requests.post('https://urlshort.in/api/url/add', headers=headers, json=json_data)
    randomLinkShort = response.json()["shorturl"]
    html = f'<html><title>QR</title><style>#qr{{height: 750px;width: 750px;position: absolute;top: 50%;left: ' \
           f'50%;-moz-transform: translateX(-50%) translateY(-50%);-webkit-transform: translateX(-50%) translateY(' \
           f'-50%);transform: translateX(-50%) translateY(-50%);}}</style><body><img ' \
           f'src="https://api.qrserver.com/v1/create-qr-code/?data={randomLinkShort}&size=10000x10000" alt="" ' \
           f'title="" id="qr"/></body></html> '
    return html


@app.route('/admin', methods=["POST", "GET"])
def admin():
    if request.method == 'POST':
        if 'username' in request.form or 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            if username == "Admin" and password == "123456":
                return render_template("adminPanel.html")
            else:
                return render_template("adminLogin.html")
        elif 'see' in request.form:
            htmlChange = json2html.convert(json=userNamesDict)
            response = make_response(render_template_string(htmlChange))
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            return response
        elif 'reset' in request.form:
            return render_template_string(resetAndQR())
        elif 'class' in request.form:
            html = f'<!DOCTYPE html><html lang="he" dir="rtl"> <title>כמות תלמידים שהיו</title> <meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <style> body {{ text-align:center; display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 100vh;}}</style> <body> <div> <h1>כמות התלמידים בשיעור האחרון:</h1> </div> <div> <h1>{len(userNamesList)}</h1> </div> </body></html>'
            return render_template_string(html)
        return render_template("adminLogin.html")
    else:
        return render_template("adminLogin.html")


## Main ##
if __name__ == '__main__':
    port = int(os.getenv('PORT', 25565))
    app.run(host='0.0.0.0', port=port, ssl_context='adhoc')
