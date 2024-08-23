import random
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField
from wtforms.validators import InputRequired, Length, EqualTo, Email
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'MSOEF'
app.config['UPLOAD_FOLDER'] = 'static/profile_photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Mock data for users and members
members = ["Mohit", "VIPIN", "vikas", "Dipak", "chirag"]
contributions = {member: [] for member in members}
loans = []
users = {
    '9649509717': {
        'first_name': 'Abhishek',
        'last_name': 'Bhatt',
        'email': 'abhishek@example.com',
        'phone_number': '9649509717',
        'dob': '1990-01-01',
        'photo': 'default.png',
        'pin': '1234'
    }
}

# Form for signup
class SignupForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[InputRequired(), Length(max=50)])
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=100)])
    phone_number = StringField('Phone Number', validators=[InputRequired(), Length(min=10, max=15)])
    dob = DateField('Date of Birth', validators=[InputRequired()], format='%Y-%m-%d')
    security_question = SelectField('Security Question', choices=[
        ('pet', 'What is your pet\'s name?'),
        ('city', 'Where were you born?'),
        ('school', 'What is the name of your first school?')
    ], validators=[InputRequired()])
    security_answer = StringField('Security Answer', validators=[InputRequired(), Length(max=100)])
    pin = PasswordField('PIN', validators=[InputRequired(), Length(min=4, max=4)])
    confirm_pin = PasswordField('Confirm PIN', validators=[InputRequired(), EqualTo('pin')])
    submit = SubmitField('Signup')

# Form for login
class LoginForm(FlaskForm):
    phone_number = StringField('Phone Number', validators=[InputRequired(), Length(min=10, max=15)])
    pin = PasswordField('PIN', validators=[InputRequired(), Length(min=4, max=4)])
    submit = SubmitField('Login')

# Form for password reset
class ForgotPasswordForm(FlaskForm):
    phone_number = StringField('Phone Number', validators=[InputRequired(), Length(min=10, max=15)])
    dob = DateField('Date of Birth', validators=[InputRequired()], format='%Y-%m-%d')
    security_question = SelectField('Security Question', choices=[
        ('pet', 'What is your pet\'s name?'),
        ('city', 'Where were you born?'),
        ('school', 'What is the name of your first school?')
    ], validators=[InputRequired()])
    security_answer = StringField('Security Answer', validators=[InputRequired(), Length(max=100)])
    new_pin = PasswordField('New PIN', validators=[InputRequired(), Length(min=4, max=4)])
    confirm_new_pin = PasswordField('Confirm New PIN', validators=[InputRequired(), EqualTo('new_pin')])
    submit = SubmitField('Reset Password')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        phone_number = form.phone_number.data
        pin = form.pin.data
        users[phone_number] = {
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'email': form.email.data,
            'dob': form.dob.data,
            'security_question': form.security_question.data,
            'security_answer': form.security_answer.data,
            'pin': pin
        }
        flash('Signup successful!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        phone_number = form.phone_number.data
        pin = form.pin.data
        if phone_number in users and users[phone_number]['pin'] == pin:
            session['phone_number'] = phone_number
            flash('Login successful!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid phone number or PIN. Please try again.', 'danger')
    return render_template('login.html', form=form)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        phone_number = form.phone_number.data
        dob = form.dob.data
        security_question = form.security_question.data
        security_answer = form.security_answer.data
        new_pin = form.new_pin.data
        confirm_new_pin = form.confirm_new_pin.data
        
        if (phone_number in users and
            users[phone_number]['dob'] == dob and
            users[phone_number]['security_question'] == security_question and
            users[phone_number]['security_answer'] == security_answer):
            users[phone_number]['pin'] = new_pin
            flash('Password reset successful!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid information. Please try again.', 'danger')
    return render_template('forgot_password.html', form=form)

@app.route('/logout')
def logout():
    session.pop('phone_number', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'phone_number' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    user = users[session['phone_number']]
    return render_template('profile.html', user=user)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'phone_number' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user = users[session['phone_number']]
    user['first_name'] = request.form['first_name']
    user['last_name'] = request.form['last_name']
    user['email'] = request.form['email']
    user['phone_number'] = request.form['phone_number']
    user['dob'] = request.form['dob']

    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename != '':
            if allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(photo_path)
                user['photo'] = filename
            else:
                flash('Invalid file type. Allowed types are png, jpg, jpeg, gif.', 'danger')
                return redirect(url_for('profile'))

    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/Monthly_Report', methods=['GET', 'POST'])
def Monthly_Report():
    if request.method == 'POST':
        group_name = request.form['group_name']
        logo = request.form['logo']
        selected_members = request.form.getlist('members')
        flash(f'Group "{group_name}" created with members: {", ".join(selected_members)}', 'success')
        return redirect(url_for('Monthly_Report'))

    return render_template('Monthly_Report.html', members=members)

@app.route('/loan', methods=['GET', 'POST'])
def loan():
    if request.method == 'POST':
        member = request.form['member']
        amount = request.form['amount']
        loans.append({'member': member, 'amount': amount})
        return redirect(url_for('loan'))
    return render_template('loan.html', loans=loans)

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/bench')
def bench():
    selected_judges = random.sample(members, 3)
    return render_template('bench.html', judges=selected_judges)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/feature')
def feature():
    return render_template('feature.html')

@app.route('/documents')
def documents():
    return render_template('documents.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
