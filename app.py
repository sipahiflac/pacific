from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file
from utils import analiz

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'home' # Redirect to landing page if not logged in
oauth = OAuth(app)

# Google OAuth Config
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=True) # Nullable for Google Auth users
    name = db.Column(db.String(1000))
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    profile_pic = db.Column(db.String(1000))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('report'))
    return render_template('landing.html')

# Auth Routes
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.password or not check_password_hash(user.password, password):
        return jsonify({'success': False, 'message': 'Hatalı email veya şifre.'}), 401
    
    login_user(user)
    return jsonify({'success': True, 'redirect': url_for('report')})

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'success': False, 'message': 'Bu email adresi zaten kayıtlı.'}), 400
    
    new_user = User(
        email=email,
        name=name,
        password=generate_password_hash(password, method='scrypt')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    login_user(new_user)
    return jsonify({'success': True, 'redirect': url_for('report')})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/google-login')
def google_login():
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def google_callback():
    try:
        token = google.authorize_access_token()
        user_info = google.userinfo()
        
        user = User.query.filter_by(email=user_info['email']).first()
        
        if not user:
            user = User(
                email=user_info['email'],
                name=user_info['name'],
                google_id=user_info['id'],
                profile_pic=user_info['picture']
            )
            db.session.add(user)
            db.session.commit()
        elif not user.google_id:
            # Link existing account
            user.google_id = user_info['id']
            user.profile_pic = user_info['picture']
            db.session.commit()
            
        login_user(user)
        return redirect(url_for('report'))
    except Exception as e:
        print(f"Google Auth Error: {e}")
        return redirect(url_for('home'))

@app.route('/report')
@login_required
def report():
    # Get all available names from data directory
    names = analiz.get_all_names()
    
    # Get selected name from query param, default to first name if available
    selected_name = request.args.get('name')
    if not selected_name and names:
        selected_name = names[0]
    
    kpi_data = {}
    top_posts = []
    city = "Sivas" # Default fallback
    chart_data = {}
    
    if selected_name:
        analysis_result = analiz.analyze_data(selected_name)
        if analysis_result:
            kpi_data = analysis_result['kpi_data']
            top_posts = analysis_result['top_posts']
            city = analysis_result.get('city', "Sivas")
            chart_data = analysis_result.get('chart_data', {})

    return render_template('index.html', names=names, selected_name=selected_name, kpi_data=kpi_data, top_posts=top_posts, city=city, chart_data=chart_data, user=current_user)

@app.route('/all-posts')
@login_required
def all_posts():
    # Only fetch regions for the filter dropdown
    # We can get regions from profile_tags.csv directly or cache them
    # For now, let's get them via analiz but optimize if needed later
    # To avoid loading all posts just for regions, we can add a helper in analiz
    # But for now, let's stick to the plan: pass regions to template
    
    # Optimization: Just get unique regions from profile_tags
    region_map = analiz.get_region_map()
    regions = sorted(list(set(region_map.values())))
    return render_template('all_posts.html', regions=regions)

@app.route('/api/all-posts')
@login_required
def api_all_posts():
    posts = analiz.get_all_posts_data()
    return jsonify({'data': posts})

@app.route('/mayors')
@login_required
def mayors():
    mayors_data = analiz.get_mayors_data()
    # Extract unique regions for the filter
    regions = sorted(list(set(m['region'] for m in mayors_data if m['region'])))
    return render_template('mayors.html', mayors=mayors_data, regions=regions)

@app.route('/axioms')
@login_required
def axioms():
    return render_template('generic_page.html', title="Yapay Zeka Aksiyomları")

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        # Check if it's a password change
        if 'new_password' in request.form:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if not current_user.password:
                flash('Google ile giriş yapan kullanıcılar şifre değiştiremez.', 'danger')
            elif not check_password_hash(current_user.password, current_password):
                flash('Mevcut şifre hatalı.', 'danger')
            elif new_password != confirm_password:
                flash('Yeni şifreler eşleşmiyor.', 'danger')
            else:
                current_user.password = generate_password_hash(new_password, method='scrypt')
                db.session.commit()
                flash('Şifreniz başarıyla güncellendi.', 'success')
        
        # Check if it's a name update (if we decide to add it back later or if hidden)
        elif 'name' in request.form:
            name = request.form.get('name')
            if name:
                current_user.name = name
                db.session.commit()
                flash('Profil bilgileriniz güncellendi.', 'success')
            else:
                flash('İsim alanı boş bırakılamaz.', 'danger')
                
        return redirect(url_for('account'))
    return render_template('account.html')

@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    user = current_user
    logout_user()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
