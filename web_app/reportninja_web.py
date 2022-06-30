import flask
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, abort
from flask_login import login_required, LoginManager, login_user, current_user, logout_user
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
import getpass
import os
import json
import pdfkit
import datetime
import zipfile
import string
import random
import shutil
import sys
from jinja2 import Environment, FileSystemLoader
from lib import test, findings, product, engagement, endpoints, jira
from lib import template as temp_config

DojoURL = ''
TestID = ''
TestName= ''
FindingsCount = ''
Product = ''
OutputFile = 'Pentest Report'
ReportTemplate = ''
JIRA = False
PDF = False
Config = ''
ID = ''

if not sys.argv[1:]:
    answer = input('[ ? ] Does an Admin need created?: ')
elif sys.argv[1] == 'no-prompt':
    answer = 'n'
else:
    answer = input('[ ? ] Does an Admin need created?: ')

if answer in ['yes', 'Yes', 'Y', 'y']:
    print('[ + ] Info for creating admin user\n')

    user_name = input('Username: ')
    password = getpass.getpass(prompt='Password: ', stream=None)
    dojo_url = input('DefectDojo URL: ')
    api_key = getpass.getpass(prompt='DefectDojo API Key: ', stream=None)
else:
    pass

UPLOAD_FOLDER = 'templates'
ALLOWED_EXTENSIONS = {'html'}

letters = string.ascii_lowercase
generated_secret = (''.join(random.choice(letters) for i in range(25)))

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = generated_secret
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

db.init_app(app)

from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    dojo_url = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)
    api_key = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

if answer in ['yes', 'Yes', 'Y', 'y']:
    user = User(username=user_name, password=generate_password_hash(password, method='pbkdf2:sha256'), dojo_url=dojo_url, admin=True, api_key=api_key)
    db.session.add(user)
    db.session.commit()
else:
    pass

login_manager = LoginManager()
login_manager.login_vew = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.errorhandler(401)
def unauthorized(e):
    return redirect(url_for('login'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        env = Environment(loader=FileSystemLoader('web_templates'))
        template = env.get_template('login.html')
        return render_template(template)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            return redirect(url_for('login'))

        login_user(user)

    return redirect(url_for('home'))


@app.route('/', methods=['GET'])
@login_required
def home():

    TemplateList = []

    for file in os.walk('../templates/'):
        for x in range(len(file[2])):
            TemplateList.append(file[2][x])

    env = Environment(loader=FileSystemLoader('web_templates'))
    template = env.get_template('index.html')

    user = User.query.filter_by(id=current_user.id).first()

    if user.admin == True:
        return template.render(templates=TemplateList, admin='admin')
    else:
        return template.render(templates=TemplateList)

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    global DojoURL
    global TestID
    global TestName
    global FindingsCount
    global Product
    global OutputFile
    global Template
    global JIRA
    global PDF
    global Config
    global ID

    user = User.query.filter_by(id=current_user.id).first()
    api_key = user.api_key
    DojoURL = user.dojo_url

    letters = string.ascii_lowercase

    ID = (datetime.datetime.now().strftime("%m-%d-%y-%I-%M") + '-' + (''.join(random.choice(letters) for i in range(10))))

    os.mkdir(('reports/' + ID))

    TestID = request.form['testid']
    if 'jira' in request.form:
        JIRA = True
    else:
        JIRA = False
    if 'pdf' in request.form:
        PDF = True
    else:
        PDF = False
    OutputFile = request.form['filename']
    Template = request.form['template']
    if request.files['template_config'].filename == '':
        Config = ''
    else:
        f = request.files['template_config']
        f.save(f'reports/{ID}/{secure_filename(f.filename)}')
        Config = ('reports/' + ID + '/' + f.filename)

    TestName = test.by_id(DojoURL, api_key, TestID)['title']

    FindingsCount = findings.finding_count(DojoURL, api_key, TestID)

    Engagement = test.by_id(DojoURL, api_key, TestID)['engagement']

    Product = product.by_id(DojoURL, api_key, engagement.by_id(DojoURL, api_key, Engagement)['product'])

    ProductType = product.product_type(DojoURL, api_key, Product['prod_type'])

    Findings = findings.by_test_id(DojoURL, api_key, TestID)

    Endpoints = {}

    for finding in Findings['results']:
        keys = []
        for x in range(0, len(finding['endpoints'])):
            keys.append(finding['endpoints'][x])

        for key in keys:
            endpoint_details = endpoints.by_id(DojoURL, api_key, key)
            endpoint = endpoint_details['protocol'] + '://' + endpoint_details['host'] + endpoint_details['path']
            Endpoints.update({str(key): endpoint})

    JiraTickets = []

    if JIRA == True:
        for x in Findings['results']:
            try:
                JiraTickets.append(jira.by_finding_id(DojoURL, api_key, x['id'])['results'][0]['jira_key'])
            except:
                JiraTickets.append('No Ticket Available')
    else:
        pass

    env = Environment(loader=FileSystemLoader('../templates'))
    template = env.get_template(Template)

    if JIRA == True:
        output = template.render(engagement= engagement.by_id(DojoURL, api_key, Engagement), product=Product, product_type=ProductType, test=test.by_id(DojoURL, api_key, TestID), findings=Findings, endpoints=Endpoints, jira=JiraTickets)
    else:
        output = template.render(engagement= engagement.by_id(DojoURL, api_key, Engagement), product=Product, product_type=ProductType, test=test.by_id(DojoURL, api_key, TestID), findings=Findings, endpoints=Endpoints)

    if PDF == True:

        options = options = {'quiet': ''}

        with open(('reports/' + ID + '/' + OutputFile + '.html'), 'w') as file:
            file.write(output)
            file.close()

        if Config != '':
            temp_config.template_config(('reports/' + ID + '/' + OutputFile + '.html'), Config)
            with open(Config, 'r') as config_file:
                contents = json.load(config_file)
                config_file.close()

            if contents['pdf']:
                options = contents['pdf']
            else:
                pass
        else:
            pass

        pdfkit.from_file(('reports/' + ID + '/' + OutputFile + '.html'), ('reports/' + ID + '/' + OutputFile + '.pdf'), options=options)

    else:

        with open(('reports/' + ID + '/' + OutputFile + '.html'), 'w') as file:
            file.write(output)
            file.close()

        if len(Config) != 0:
            temp_config.template_config(('reports/' + ID + '/' + OutputFile + '.html'), Config)
        else:
            pass

    return redirect(url_for('report', ReportName=OutputFile))


@app.route('/report/<ReportName>', methods=['GET'])
@login_required
def report(ReportName):
    env = Environment(loader=FileSystemLoader('web_templates'))
    template = env.get_template('reportview.html')

    user = User.query.filter_by(id=current_user.id).first()

    if user.admin == True:
        return render_template(template, report=((ID + '/' + ReportName)), admin='admin')
    else:
        return render_template(template, report=((ID + '/' + ReportName)))

@app.route('/report/<ID>/<ReportName>', methods=['GET'])
@login_required
def report_preview(ID,ReportName):
    env = Environment(loader=FileSystemLoader(('reports/' + ID)))
    template = env.get_template((ReportName + '.html'))
    return render_template(template)

@app.route('/report/download', methods=['GET'])
@login_required
def report_download():
    package = zipfile.ZipFile(str('reports/' + ID + '/' + 'package.zip'), 'w')
    for file in os.walk(('reports/' + ID)):
        for x in range(len(file[2])):
            if file[2][x] != 'package.zip':
                filename = str('reports/' + str(ID) + '/' + file[2][x])
                package.write(filename)
    package.close()
    path = ('reports/' + str(ID) + '/')

    return send_from_directory(path, 'package.zip')

@app.route('/report/delete', methods=['GET'])
@login_required
def report_delete():
    shutil.rmtree(('reports/' + ID))
    return redirect(url_for('home'))

@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    user = User.query.filter_by(id=current_user.id).first()
    if request.method == 'GET':
        env = Environment(loader=FileSystemLoader('web_templates'))
        template = env.get_template('profile.html')

        if user.admin == True:
            return template.render(user=user.username, dojo_url=user.dojo_url, api_key=user.api_key, admin='admin')
        else:
            return template.render(user=user.username, dojo_url=user.dojo_url, api_key=user.api_key,)

    if request.method == 'POST':

        if request.form['password'] != '':
            user.password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        else:
            pass

        if request.form['url'] != '':
            user.dojo_url = request.form['url']
        else:
            pass

        if request.form['api_key'] != '':
            user.api_key = request.form['api_key']
        else:
            pass

        db.session.commit()

        env = Environment(loader=FileSystemLoader('web_templates'))
        template = env.get_template('profile.html')

        if user.admin == True:
            return template.render(user=user.username, dojo_url=user.dojo_url, api_key=user.api_key, admin='admin')
        else:
            return template.render(user=user.username, dojo_url=user.dojo_url, api_key=user.api_key,)

@app.route('/admin', methods=['GET'])
@login_required
def admin():
    user = User.query.filter_by(id=current_user.id).first()
    if user.admin == True:

        TemplateList = []

        for file in os.walk('../templates/'):
            for x in range(len(file[2])):
                TemplateList.append(file[2][x])

        all_users = User.query.all()

        env = Environment(loader=FileSystemLoader('web_templates'))
        template = env.get_template('admin.html')
        return template.render(templates=TemplateList, users=all_users)
    else:
        return redirect(url_for('home'))

@app.route('/admin/template/upload', methods=['GET', 'POST'])
@login_required
def admin_template_upload():
    user = User.query.filter_by(id=current_user.id).first()
    if request.method == 'GET':
        if user.admin == True:
            env = Environment(loader=FileSystemLoader('web_templates'))
            template = env.get_template('admin.html')
            return render_template(template)
        else:
            return redirect(url_for('home'))

    if request.method == 'POST':
        if user.admin == True:
            f = request.files['template']
            if f.filename.split('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                f.save(f'../templates/{secure_filename(f.filename)}')
                return redirect(url_for('admin'))
            else:
                abort(400)
        else:
            return redirect(url_for('home'))

@app.route('/admin/template/delete', methods=['POST'])
@login_required
def admin_template_delete():
    user = User.query.filter_by(id=current_user.id).first()
    if user.admin == True:
        os.remove(('../templates/' + request.form['template']))
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('home'))

@app.route('/admin/user/create', methods=['POST'])
@login_required
def admin_user_create():
    user = User.query.filter_by(id=current_user.id).first()
    if user.admin == True:
        if 'admin' in request.form:
            new_user = User(username=request.form['username'], password=generate_password_hash(request.form['password'], method='pbkdf2:sha256'), dojo_url=request.form['url'], admin=True, api_key=request.form['api_key'])
        else:
            new_user = User(username=request.form['username'], password=generate_password_hash(request.form['password'], method='pbkdf2:sha256'), dojo_url=request.form['url'], admin=False, api_key=request.form['api_key'])

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('admin'))
    else:
        return redirect(url_for('home'))

@app.route('/admin/user/delete', methods=['POST'])
@login_required
def admin_user_delete():
    user = User.query.filter_by(id=current_user.id).first()
    if user.admin == True:
        User.query.filter_by(username=request.form['user']).delete()
        db.session.commit()

        return redirect(url_for('admin'))
    else:
        return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(port='8000',host='0.0.0.0')
