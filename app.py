from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Post, Comment, PostFollow
from config import Config
import secrets
import os
import uuid
from werkzeug.utils import secure_filename
from sqlalchemy import and_

# Tạo thư mục instance nếu chưa tồn tại
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

# Thêm cấu hình cho upload ảnh
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Tạo thư mục uploads nếu chưa tồn tại
os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)

db.init_app(app)

# Thiết lập Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Hàm kiểm tra file có hợp lệ không
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
# Hàm tạo tên file độc nhất
def generate_unique_filename(filename):
    _, ext = os.path.splitext(filename)
    return f"{uuid.uuid4().hex}{ext}"

# Middleware kiểm tra người dùng bị khóa
@app.before_request
def check_blocked_user():
    if current_user.is_authenticated and current_user.is_blocked:
        logout_user()
        return redirect(url_for('blocked'))


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

# Cập nhật route new_post để xử lý upload ảnh
@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        if not title or not content:
            flash('Tiêu đề và nội dung không được để trống!', 'danger')
            return render_template('new_post.html')
        
        # Khởi tạo post với giá trị mặc định image_file=None
        post = Post(title=title, content=content, author=current_user)
        
        # Xử lý file ảnh nếu có
        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename != '':
                if allowed_file(image.filename):
                    # Tạo tên file an toàn và độc nhất
                    filename = secure_filename(image.filename)
                    unique_filename = generate_unique_filename(filename)
                    
                    # Lưu file
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    image.save(os.path.join(app.root_path, image_path))
                    
                    # Lưu tên file vào database
                    post.image_file = unique_filename
                else:
                    flash('Định dạng file không được hỗ trợ! Chỉ chấp nhận PNG, JPG, JPEG, GIF.', 'danger')
                    return render_template('new_post.html')
        
        db.session.add(post)
        db.session.commit()
        
        flash('Bài viết của bạn đã được đăng thành công!', 'success')
        return redirect(url_for('my_posts'))
    
    return render_template('new_post.html')

# Cập nhật route edit_post để xử lý cập nhật ảnh
@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Kiểm tra quyền
    if post.user_id != current_user.id and not current_user.is_admin:
        flash('Bạn không có quyền sửa bài viết này!', 'danger')
        return redirect(url_for('post', post_id=post.id))
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        
        # Xử lý xóa ảnh hiện tại nếu được yêu cầu
        if 'remove_image' in request.form and post.image_file:
            # Xóa file ảnh khỏi thư mục
            try:
                os.remove(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], post.image_file))
            except Exception as e:
                # Xử lý ngoại lệ nếu không thể xóa file
                print(f"Error deleting file: {e}")
            
            # Đặt trường image_file thành None
            post.image_file = None
        
        # Xử lý upload ảnh mới
        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename != '':
                if allowed_file(image.filename):
                    # Xóa ảnh cũ nếu có
                    if post.image_file:
                        try:
                            os.remove(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], post.image_file))
                        except Exception as e:
                            print(f"Error deleting old file: {e}")
                    
                    # Tạo tên file an toàn và độc nhất
                    filename = secure_filename(image.filename)
                    unique_filename = generate_unique_filename(filename)
                    
                    # Lưu file
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    image.save(os.path.join(app.root_path, image_path))
                    
                    # Cập nhật tên file trong database
                    post.image_file = unique_filename
                else:
                    flash('Định dạng file không được hỗ trợ! Chỉ chấp nhận PNG, JPG, JPEG, GIF.', 'danger')
                    return render_template('edit_post.html', post=post)
        
        db.session.commit()
        
        flash('Bài viết đã được cập nhật thành công!', 'success')
        return redirect(url_for('post', post_id=post.id))
    
    return render_template('edit_post.html', post=post)

# Cập nhật route delete_post để xóa cả ảnh
@app.route('/post/<int:post_id>/delete')
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Kiểm tra quyền
    if post.user_id != current_user.id and not current_user.is_admin:
        flash('Bạn không có quyền xóa bài viết này!', 'danger')
        return redirect(url_for('post', post_id=post.id))
    
    # Xóa file ảnh nếu có
    if post.image_file:
        try:
            os.remove(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], post.image_file))
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Bài viết đã được xóa!', 'success')
    return redirect(url_for('my_posts'))

@app.route('/user-info')
def user_info():
    data = {
        'is_authenticated': current_user.is_authenticated,
        'anonymous': current_user.is_anonymous
    }
    
    if current_user.is_authenticated:
        data.update({
            'id': current_user.id,
            'username': current_user.username,
            'is_admin': current_user.is_admin
        })
    
    return render_template('debug.html', user_info=data)

@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        content = request.form['content']
        
        if not content:
            flash('Nội dung bình luận không được để trống!', 'danger')
            return redirect(url_for('post', post_id=post_id))
        
        # Thêm check để đảm bảo người dùng không bị khóa
        if current_user.is_blocked:
            flash('Tài khoản của bạn đã bị khóa và không thể bình luận.', 'danger')
            return redirect(url_for('blocked'))
            
        from models import Comment
        
        comment = Comment(
            content=content,
            user_id=current_user.id,
            post_id=post_id
        )
        
        db.session.add(comment)
        db.session.commit()
        
        flash('Bình luận của bạn đã được đăng thành công!', 'success')
    
    return redirect(url_for('post', post_id=post_id))

# Cập nhật bulk_delete_posts để xóa cả ảnh
@app.route('/bulk-delete-posts', methods=['POST'])
@login_required
def bulk_delete_posts():
    post_ids = request.form.getlist('post_ids')
    
    if not post_ids:
        flash('Không có bài viết nào được chọn để xóa.', 'warning')
        return redirect(url_for('my_posts'))
    
    deleted_count = 0
    unauthorized_count = 0
    
    for post_id in post_ids:
        post = Post.query.get(post_id)
        
        if post:
            # Kiểm tra quyền xóa (chỉ owner hoặc admin)
            if post.user_id == current_user.id or current_user.is_admin:
                # Xóa file ảnh nếu có
                if post.image_file:
                    try:
                        os.remove(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], post.image_file))
                    except Exception as e:
                        print(f"Error deleting file: {e}")
                
                db.session.delete(post)
                deleted_count += 1
            else:
                unauthorized_count += 1
                
    if unauthorized_count > 0:
        flash(f'Có {unauthorized_count} bài viết bạn không có quyền xóa.', 'warning')
    
    if deleted_count > 0:
        db.session.commit()
        flash(f'Đã xóa thành công {deleted_count} bài viết.', 'success')
    
    return redirect(url_for('my_posts'))

@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def index(page):
    per_page = 5
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('index.html', posts=posts)

@app.route('/my-posts', defaults={'page': 1})
@app.route('/my-posts/page/<int:page>')
@login_required
def my_posts(page):
    per_page = 5
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('my_posts.html', posts=posts)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Kiểm tra mật khẩu hiện tại
        if not check_password_hash(current_user.password, current_password):
            flash('Mật khẩu hiện tại không chính xác!', 'danger')
            return render_template('change_password.html')
        
        # Kiểm tra mật khẩu mới và xác nhận mật khẩu
        if new_password != confirm_password:
            flash('Mật khẩu mới và xác nhận mật khẩu không khớp!', 'danger')
            return render_template('change_password.html')
        
        # Kiểm tra độ dài mật khẩu mới (tuỳ chọn)
        if len(new_password) < 6:
            flash('Mật khẩu mới phải có ít nhất 6 ký tự!', 'danger')
            return render_template('change_password.html')
        
        # Cập nhật mật khẩu mới
        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        
        flash('Mật khẩu của bạn đã được cập nhật thành công!', 'success')
        return redirect(url_for('index'))
    
    return render_template('change_password.html')

# Thêm route để theo dõi bài viết
@app.route('/post/<int:post_id>/follow')
@login_required
def follow_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Kiểm tra người dùng không tự follow bài của mình
    if post.user_id == current_user.id:
        flash('Bạn không thể theo dõi bài viết của chính mình.', 'warning')
        return redirect(url_for('post', post_id=post_id))
    
    # Kiểm tra xem người dùng đã theo dõi bài viết này chưa
    existing_follow = PostFollow.query.filter(
        and_(
            PostFollow.user_id == current_user.id,
            PostFollow.post_id == post_id
        )
    ).first()
    
    if existing_follow:
        flash('Bạn đã theo dõi bài viết này rồi.', 'info')
    else:
        # Tạo đối tượng theo dõi mới
        follow = PostFollow(user_id=current_user.id, post_id=post_id)
        db.session.add(follow)
        db.session.commit()
        flash('Bạn đã theo dõi bài viết thành công!', 'success')
    
    return redirect(url_for('post', post_id=post_id))

# Thêm route để bỏ theo dõi bài viết
@app.route('/post/<int:post_id>/unfollow')
@login_required
def unfollow_post(post_id):
    # Tìm và xóa đối tượng theo dõi
    follow = PostFollow.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()
    
    if follow:
        db.session.delete(follow)
        db.session.commit()
        flash('Bạn đã bỏ theo dõi bài viết thành công!', 'success')
    else:
        flash('Bạn chưa theo dõi bài viết này.', 'info')
    
    return redirect(url_for('post', post_id=post_id))

# Thêm route để xem danh sách bài viết đã theo dõi
@app.route('/followed-posts', defaults={'page': 1})
@app.route('/followed-posts/page/<int:page>')
@login_required
def followed_posts(page):
    per_page = 5
    
    # Lấy danh sách ID bài viết mà người dùng đã theo dõi
    followed_post_ids = db.session.query(PostFollow.post_id).filter_by(user_id=current_user.id).all()
    followed_post_ids = [post_id[0] for post_id in followed_post_ids]
    
    # Lấy thông tin chi tiết các bài viết đã theo dõi
    posts = Post.query.filter(Post.id.in_(followed_post_ids)).order_by(Post.date_posted.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('followed_posts.html', posts=posts)

if __name__ == '__main__':
    with app.app_context():
        # Import models để migration database
        from models import User, Post, Comment, PostFollow
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
            
    app.run(host='0.0.0.0', debug=True)