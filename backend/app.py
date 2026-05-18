"""
肴柒蟹 - Flask 主应用
注册 / 登录 / 养殖户塘口监控 / 养殖日志管理
"""

import os
import sys
from datetime import datetime, date, timezone

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, abort
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from werkzeug.security import generate_password_hash

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from models import db, User, Pond, EnvData, FarmingLog

app = Flask(__name__)
app.config.from_object(Config)

# 静态文件路径指向上级目录（共享 style.css / script.js）
app.static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
app.static_url_path = '/static'

# 初始化扩展
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录后再访问'
login_manager.login_message_category = 'warning'


# =============================================
# 用户加载回调
# =============================================
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# =============================================
# 创建数据库表
# =============================================
with app.app_context():
    db.create_all()


# =============================================
# 首页 - 后端仪表盘重定向
# =============================================
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# =============================================
# 注册
# =============================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        role = request.form.get('role', 'farmer')
        real_name = request.form.get('real_name', '').strip()
        farm_address = request.form.get('farm_address', '').strip()

        # 验证
        errors = []
        if not username or len(username) < 2:
            errors.append('用户名至少2个字符')
        if not phone:
            errors.append('手机号为必填项')
        if email and '@' not in email:
            errors.append('邮箱格式不正确')
        if not password or len(password) < 6:
            errors.append('密码至少6个字符')
        if password != password_confirm:
            errors.append('两次密码输入不一致')
        if role not in ('farmer', 'consumer'):
            errors.append('请选择用户类型')

        if not errors:
            if User.query.filter_by(username=username).first():
                errors.append('该用户名已被注册')
            elif phone:
                if User.query.filter_by(phone=phone).first():
                    errors.append('该手机号已被注册')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('register.html', form=request.form)

        # 创建用户
        user = User(
            username=username,
            email=email,
            phone=phone,
            role=role,
            real_name=real_name or None,
            farm_address=farm_address or None,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('注册成功！请登录', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form={})


# =============================================
# 登录
# =============================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=bool(remember))
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()

            flash(f'欢迎回来，{user.username}！', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('用户名或密码错误', 'danger')

    return render_template('login.html')


# =============================================
# 退出登录
# =============================================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('login'))


# =============================================
# 养殖户仪表盘
# =============================================
@app.route('/dashboard')
@login_required
def dashboard():
    ponds = Pond.query.filter_by(user_id=current_user.id).order_by(Pond.created_at.desc()).all()

    # 统计概览
    stats = {
        'pond_count': len(ponds),
        'total_area': sum(p.area or 0 for p in ponds),
        'latest_log': None,
    }

    # 获取最近的一条日志
    latest_log = FarmingLog.query.join(Pond).filter(
        Pond.user_id == current_user.id
    ).order_by(FarmingLog.log_date.desc()).first()
    if latest_log:
        stats['latest_log'] = latest_log.to_dict()

    return render_template('dashboard.html', ponds=ponds, stats=stats)


# =============================================
# 添加塘口
# =============================================
@app.route('/pond/add', methods=['GET', 'POST'])
@login_required
def add_pond():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('请输入塘口名称', 'danger')
            return render_template('pond_form.html', form=request.form)

        pond = Pond(
            user_id=current_user.id,
            name=name,
            location=request.form.get('location', '').strip(),
            area=request.form.get('area', type=float),
            species=request.form.get('species', '').strip(),
            stock_density=request.form.get('stock_density', type=int),
            water_depth=request.form.get('water_depth', type=float),
            aeration=bool(request.form.get('aeration')),
            notes=request.form.get('notes', '').strip(),
        )
        db.session.add(pond)
        db.session.commit()
        flash(f'塘口「{name}」添加成功', 'success')
        return redirect(url_for('dashboard'))

    return render_template('pond_form.html', form={}, pond=None)


# =============================================
# 编辑塘口
# =============================================
@app.route('/pond/<int:pond_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_pond(pond_id):
    pond = db.session.get(Pond, pond_id)
    if not pond or pond.user_id != current_user.id:
        abort(404)

    if request.method == 'POST':
        pond.name = request.form.get('name', '').strip()
        pond.location = request.form.get('location', '').strip()
        pond.area = request.form.get('area', type=float)
        pond.species = request.form.get('species', '').strip()
        pond.stock_density = request.form.get('stock_density', type=int)
        pond.water_depth = request.form.get('water_depth', type=float)
        pond.aeration = bool(request.form.get('aeration'))
        pond.notes = request.form.get('notes', '').strip()
        db.session.commit()
        flash(f'塘口「{pond.name}」已更新', 'success')
        return redirect(url_for('dashboard'))

    return render_template('pond_form.html', form=pond, pond=pond)


# =============================================
# 删除塘口
# =============================================
@app.route('/pond/<int:pond_id>/delete', methods=['POST'])
@login_required
def delete_pond(pond_id):
    pond = db.session.get(Pond, pond_id)
    if not pond or pond.user_id != current_user.id:
        abort(404)

    name = pond.name
    db.session.delete(pond)
    db.session.commit()
    flash(f'塘口「{name}」已删除', 'info')
    return redirect(url_for('dashboard'))


# =============================================
# 塘口详情 - 环境监控 + 养殖日志
# =============================================
@app.route('/pond/<int:pond_id>')
@login_required
def pond_detail(pond_id):
    pond = db.session.get(Pond, pond_id)
    if not pond or pond.user_id != current_user.id:
        abort(404)

    # 获取最新环境数据
    latest_env = EnvData.query.filter_by(pond_id=pond_id)\
        .order_by(EnvData.recorded_at.desc()).first()

    # 获取最近7天的环境数据（用于图表）→ 转为 dict 以支持 tojson
    env_history = EnvData.query.filter_by(pond_id=pond_id)\
        .order_by(EnvData.recorded_at.desc()).limit(7).all()
    env_history.reverse()
    env_history_dicts = [e.to_dict() for e in env_history]

    # 获取养殖日志 → 转为 dict
    logs = FarmingLog.query.filter_by(pond_id=pond_id)\
        .order_by(FarmingLog.log_date.desc()).all()
    logs_dicts = [l.to_dict() for l in logs]

    return render_template(
        'pond_detail.html',
        pond=pond,
        latest_env=latest_env,
        env_history=env_history_dicts,
        logs=logs_dicts,
    )


# =============================================
# 添加环境数据（手动）
# =============================================
@app.route('/pond/<int:pond_id>/env/add', methods=['POST'])
@login_required
def add_env_data(pond_id):
    pond = db.session.get(Pond, pond_id)
    if not pond or pond.user_id != current_user.id:
        abort(404)

    data = EnvData(
        pond_id=pond_id,
        temperature=request.form.get('temperature', type=float),
        dissolved_oxygen=request.form.get('dissolved_oxygen', type=float),
        ph_value=request.form.get('ph_value', type=float),
        ammonia=request.form.get('ammonia', type=float),
        salinity=request.form.get('salinity', type=float),
        turbidity=request.form.get('turbidity', type=float),
        source='manual',
    )
    db.session.add(data)
    db.session.commit()
    flash('环境数据已记录', 'success')
    return redirect(url_for('pond_detail', pond_id=pond_id))


# =============================================
# 添加养殖日志
# =============================================
@app.route('/pond/<int:pond_id>/log/add', methods=['POST'])
@login_required
def add_farming_log(pond_id):
    pond = db.session.get(Pond, pond_id)
    if not pond or pond.user_id != current_user.id:
        abort(404)

    log = FarmingLog(
        pond_id=pond_id,
        log_date=datetime.now(timezone.utc).date(),
        feeding_amount=request.form.get('feeding_amount', type=float),
        feed_protein=request.form.get('feed_protein', type=float),
        mortality=request.form.get('mortality', type=float),
        stock_count=request.form.get('stock_count', type=int),
        molting_status=request.form.get('molting_status', '').strip() or None,
        water_temperature=request.form.get('water_temperature', type=float),
        weather=request.form.get('weather', '').strip() or None,
        medication=request.form.get('medication', '').strip() or None,
        notes=request.form.get('notes', '').strip() or None,
    )
    db.session.add(log)
    db.session.commit()
    flash('养殖日志已记录', 'success')
    return redirect(url_for('pond_detail', pond_id=pond_id))


# =============================================
# API: 获取环境数据（图表用）
# =============================================
@app.route('/api/pond/<int:pond_id>/env')
@login_required
def api_env_data(pond_id):
    pond = db.session.get(Pond, pond_id)
    if not pond or pond.user_id != current_user.id:
        return jsonify({'error': 'unauthorized'}), 403

    days = request.args.get('days', 7, type=int)
    data = EnvData.query.filter_by(pond_id=pond_id)\
        .filter(EnvData.recorded_at >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0) - __import__('datetime').timedelta(days=days))\
        .order_by(EnvData.recorded_at.asc()).all()

    return jsonify({
        'pond': pond.name,
        'data': [d.to_dict() for d in data],
        'count': len(data),
    })


# =============================================
# API: 获取养殖日志
# =============================================
@app.route('/api/pond/<int:pond_id>/logs')
@login_required
def api_farming_logs(pond_id):
    pond = db.session.get(Pond, pond_id)
    if not pond or pond.user_id != current_user.id:
        return jsonify({'error': 'unauthorized'}), 403

    logs = FarmingLog.query.filter_by(pond_id=pond_id)\
        .order_by(FarmingLog.log_date.desc()).limit(30).all()

    return jsonify({
        'pond': pond.name,
        'logs': [l.to_dict() for l in logs],
    })


# =============================================
# 启动
# =============================================
if __name__ == '__main__':
    print('🦀 肴柒蟹 后端已启动')
    print(f'   📂 数据库: {app.config["SQLALCHEMY_DATABASE_URI"]}')
    print(f'   🌐 访问地址: http://127.0.0.1:5000')
    print(f'   📝 注册: http://127.0.0.1:5000/register')
    print(f'   🔑 登录: http://127.0.0.1:5000/login')
    app.run(debug=True, host='127.0.0.1', port=5000)
