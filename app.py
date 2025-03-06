from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Post
from config import Config
import secrets

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Thiết lập Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Middleware kiểm tra người dùng bị khóa
@app.before_request
def check_blocked_user():
    if current_user.is_authenticated and current_user.is_blocked:
        logout_user()
        return redirect(url_for('blocked'))

@app.route('/')
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            if user.is_blocked:
                flash('Tài khoản của bạn đã bị khóa.', 'danger')
                return redirect(url_for('blocked'))
            
            login_user(user)
            # Nếu là admin, chuyển đến trang admin dashboard
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            # Nếu là user thường, chuyển đến trang chủ
            return redirect(url_for('index'))
        else:
            flash('Đăng nhập không thành công. Kiểm tra lại tên đăng nhập hoặc mật khẩu.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất thành công.', 'success')
    return redirect(url_for('index'))

@app.route('/blocked')
def blocked():
    return render_template('blocked.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Kiểm tra xem người dùng đã tồn tại chưa
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Tên đăng nhập đã tồn tại!', 'danger')
            return render_template('register.html')
            
        # Tạo user mới
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Bạn không có quyền truy cập trang này!', 'danger')
        return redirect(url_for('index'))
        
    user_count = User.query.count()
    post_count = Post.query.count()
    blocked_count = User.query.filter_by(is_blocked=True).count()
    
    return render_template('admin/dashboard.html', 
                           user_count=user_count, 
                           post_count=post_count, 
                           blocked_count=blocked_count)

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Bạn không có quyền truy cập trang này!', 'danger')
        return redirect(url_for('index'))
        
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/block/<int:user_id>')
@login_required
def admin_block_user(user_id):
    if not current_user.is_admin:
        flash('Bạn không có quyền thực hiện hành động này!', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    # Không thể khóa tài khoản admin khác
    if user.is_admin:
        flash('Không thể khóa tài khoản admin khác!', 'danger')
        return redirect(url_for('admin_users'))
    
    user.is_blocked = True
    db.session.commit()
    
    flash(f'Tài khoản {user.username} đã bị khóa.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/unblock/<int:user_id>')
@login_required
def admin_unblock_user(user_id):
    if not current_user.is_admin:
        flash('Bạn không có quyền thực hiện hành động này!', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    user.is_blocked = False
    db.session.commit()
    
    flash(f'Tài khoản {user.username} đã được mở khóa.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/reset-password/<int:user_id>')
@login_required
def admin_reset_password(user_id):
    if not current_user.is_admin:
        flash('Bạn không có quyền thực hiện hành động này!', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    # Tạo mật khẩu ngẫu nhiên
    new_password = secrets.token_urlsafe(12)
    user.password = generate_password_hash(new_password)
    
    db.session.commit()
    
    flash(f'Mật khẩu mới cho {user.username} là: {new_password}', 'success')
    return redirect(url_for('admin_users'))

@app.context_processor
def inject_current_year():
    from datetime import datetime
    return {'current_year': datetime.now().year}

@app.route('/debug')
def debug():
    is_authenticated = current_user.is_authenticated
    user_info = {
        'is_authenticated': is_authenticated
    }
    
    if is_authenticated:
        user_info.update({
            'id': current_user.id,
            'username': current_user.username,
            'is_admin': current_user.is_admin
        })
    
    return render_template('debug.html', user_info=user_info)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Tạo tài khoản admin mặc định nếu chưa có
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            
    app.run(debug=True)