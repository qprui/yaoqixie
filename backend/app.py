"""
肴柒蟹 - REST API 服务
前后端分离，使用 JWT 认证
"""
import os
import sys
from datetime import datetime, timezone, timedelta

from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity,
    get_jwt, set_access_cookies, unset_jwt_cookies
)
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config
from models import db, User, Pond, EnvData, FarmingLog


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化扩展
    db.init_app(app)
    jwt = JWTManager(app)

    # CORS - 允许前端跨域请求
    origins = [o.strip() for o in app.config['CORS_ORIGINS'].split(',')]
    CORS(app, origins=origins, supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

    # 创建表
    with app.app_context():
        db.create_all()

    # =============================================
    # 辅助函数
    # =============================================
    def get_current_user():
        """获取当前 JWT 身份对应的用户"""
        user_id = get_jwt_identity()
        if not user_id:
            return None
        return db.session.get(User, user_id)

    def pond_belongs_to_user(pond_id, user_id):
        """检查塘口是否属于当前用户"""
        pond = db.session.get(Pond, pond_id)
        if not pond or pond.user_id != user_id:
            return None
        return pond

    # =============================================
    # 健康检查
    # =============================================
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'ok', 'service': 'yaoqixie-api'})

    # =============================================
    # 注册
    # =============================================
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请提供注册信息'}), 400

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        password_confirm = data.get('password_confirm', '')
        role = data.get('role', 'farmer')
        real_name = data.get('real_name', '').strip()
        farm_address = data.get('farm_address', '').strip()

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
        if role not in ('farmer', 'consumer', 'expert'):
            errors.append('请选择有效的用户类型')

        if not errors:
            if User.query.filter_by(username=username).first():
                errors.append('该用户名已被注册')
            elif phone:
                if User.query.filter_by(phone=phone).first():
                    errors.append('该手机号已被注册')

        if errors:
            return jsonify({'success': False, 'message': '; '.join(errors)}), 400

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

        return jsonify({'success': True, 'message': '注册成功，请登录'})

    # =============================================
    # 登录
    # =============================================
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请提供登录信息'}), 400

        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({'success': False, 'message': '请输入用户名和密码'}), 400

        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if user and user.check_password(password):
            if not user.is_active:
                return jsonify({'success': False, 'message': '账号已被禁用'}), 403

            # 更新登录时间
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()

            # 生成 JWT
            access_token = create_access_token(
                identity=user.id,
                additional_claims={
                    'username': user.username,
                    'role': user.role,
                }
            )

            return jsonify({
                'success': True,
                'message': f'欢迎回来，{user.username}！',
                'token': access_token,
                'user': user.to_dict(),
            })

        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

    # =============================================
    # 获取当前用户信息
    # =============================================
    @app.route('/api/user/me', methods=['GET'])
    @jwt_required()
    def get_user_info():
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        return jsonify({'success': True, 'user': user.to_dict()})

    # =============================================
    # 仪表盘
    # =============================================
    @app.route('/api/dashboard', methods=['GET'])
    @jwt_required()
    def dashboard():
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        ponds = Pond.query.filter_by(user_id=user.id)\
            .order_by(Pond.created_at.desc()).all()

        # 统计
        stats = {
            'pond_count': len(ponds),
            'total_area': sum(p.area or 0 for p in ponds),
            'latest_log': None,
        }

        latest_log = FarmingLog.query.join(Pond).filter(
            Pond.user_id == user.id
        ).order_by(FarmingLog.log_date.desc()).first()
        if latest_log:
            stats['latest_log'] = latest_log.to_dict()

        return jsonify({
            'success': True,
            'ponds': [p.to_dict() for p in ponds],
            'stats': stats,
            'user': user.to_dict(),
        })

    # =============================================
    # 塘口 CRUD
    # =============================================
    @app.route('/api/ponds', methods=['GET'])
    @jwt_required()
    def list_ponds():
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        ponds = Pond.query.filter_by(user_id=user.id)\
            .order_by(Pond.created_at.desc()).all()
        return jsonify({
            'success': True,
            'ponds': [p.to_dict() for p in ponds],
        })

    @app.route('/api/ponds', methods=['POST'])
    @jwt_required()
    def create_pond():
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请提供塘口信息'}), 400

        name = data.get('name', '').strip()
        if not name:
            return jsonify({'success': False, 'message': '请输入塘口名称'}), 400

        pond = Pond(
            user_id=user.id,
            name=name,
            location=data.get('location', '').strip(),
            area=data.get('area', type=float),
            species=data.get('species', '').strip(),
            stock_density=data.get('stock_density', type=int),
            water_depth=data.get('water_depth', type=float),
            aeration=bool(data.get('aeration', False)),
            notes=data.get('notes', '').strip(),
        )
        db.session.add(pond)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'塘口「{name}」添加成功',
            'pond': pond.to_dict(),
        }), 201

    @app.route('/api/ponds/<int:pond_id>', methods=['GET'])
    @jwt_required()
    def get_pond(pond_id):
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        pond = pond_belongs_to_user(pond_id, user.id)
        if not pond:
            return jsonify({'success': False, 'message': '塘口不存在'}), 404

        # 最新环境数据
        latest_env = EnvData.query.filter_by(pond_id=pond_id)\
            .order_by(EnvData.recorded_at.desc()).first()

        # 最近7天环境趋势
        env_history = EnvData.query.filter_by(pond_id=pond_id)\
            .order_by(EnvData.recorded_at.desc()).limit(7).all()
        env_history.reverse()

        # 养殖日志
        logs = FarmingLog.query.filter_by(pond_id=pond_id)\
            .order_by(FarmingLog.log_date.desc()).all()

        return jsonify({
            'success': True,
            'pond': pond.to_dict(),
            'latest_env': latest_env.to_dict() if latest_env else None,
            'env_history': [e.to_dict() for e in env_history],
            'logs': [l.to_dict() for l in logs],
        })

    @app.route('/api/ponds/<int:pond_id>', methods=['PUT'])
    @jwt_required()
    def update_pond(pond_id):
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        pond = pond_belongs_to_user(pond_id, user.id)
        if not pond:
            return jsonify({'success': False, 'message': '塘口不存在'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请提供塘口信息'}), 400

        name = data.get('name', '').strip()
        if not name:
            return jsonify({'success': False, 'message': '请输入塘口名称'}), 400

        pond.name = name
        pond.location = data.get('location', '').strip()
        pond.area = data.get('area', type=float)
        pond.species = data.get('species', '').strip()
        pond.stock_density = data.get('stock_density', type=int)
        pond.water_depth = data.get('water_depth', type=float)
        pond.aeration = bool(data.get('aeration', False))
        pond.notes = data.get('notes', '').strip()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'塘口「{pond.name}」已更新',
            'pond': pond.to_dict(),
        })

    @app.route('/api/ponds/<int:pond_id>', methods=['DELETE'])
    @jwt_required()
    def delete_pond(pond_id):
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        pond = pond_belongs_to_user(pond_id, user.id)
        if not pond:
            return jsonify({'success': False, 'message': '塘口不存在'}), 404

        name = pond.name
        db.session.delete(pond)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'塘口「{name}」已删除',
        })

    # =============================================
    # 环境数据
    # =============================================
    @app.route('/api/ponds/<int:pond_id>/env', methods=['GET'])
    @jwt_required()
    def get_env_data(pond_id):
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        pond = pond_belongs_to_user(pond_id, user.id)
        if not pond:
            return jsonify({'success': False, 'message': '塘口不存在'}), 404

        days = request.args.get('days', 7, type=int)
        since = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
        data = EnvData.query.filter_by(pond_id=pond_id)\
            .filter(EnvData.recorded_at >= since)\
            .order_by(EnvData.recorded_at.asc()).all()

        return jsonify({
            'success': True,
            'pond': pond.name,
            'data': [d.to_dict() for d in data],
            'count': len(data),
        })

    @app.route('/api/ponds/<int:pond_id>/env', methods=['POST'])
    @jwt_required()
    def add_env_data(pond_id):
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        pond = pond_belongs_to_user(pond_id, user.id)
        if not pond:
            return jsonify({'success': False, 'message': '塘口不存在'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请提供环境数据'}), 400

        env = EnvData(
            pond_id=pond_id,
            temperature=data.get('temperature', type=float),
            dissolved_oxygen=data.get('dissolved_oxygen', type=float),
            ph_value=data.get('ph_value', type=float),
            ammonia=data.get('ammonia', type=float),
            salinity=data.get('salinity', type=float),
            turbidity=data.get('turbidity', type=float),
            source='manual',
        )
        db.session.add(env)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '环境数据已记录',
            'data': env.to_dict(),
        })

    # =============================================
    # 养殖日志
    # =============================================
    @app.route('/api/ponds/<int:pond_id>/logs', methods=['GET'])
    @jwt_required()
    def get_farming_logs(pond_id):
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        pond = pond_belongs_to_user(pond_id, user.id)
        if not pond:
            return jsonify({'success': False, 'message': '塘口不存在'}), 404

        logs = FarmingLog.query.filter_by(pond_id=pond_id)\
            .order_by(FarmingLog.log_date.desc()).limit(30).all()

        return jsonify({
            'success': True,
            'pond': pond.name,
            'logs': [l.to_dict() for l in logs],
        })

    @app.route('/api/ponds/<int:pond_id>/logs', methods=['POST'])
    @jwt_required()
    def add_farming_log(pond_id):
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        pond = pond_belongs_to_user(pond_id, user.id)
        if not pond:
            return jsonify({'success': False, 'message': '塘口不存在'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请提供养殖日志数据'}), 400

        log = FarmingLog(
            pond_id=pond_id,
            log_date=datetime.now(timezone.utc).date(),
            feeding_amount=data.get('feeding_amount', type=float),
            feed_protein=data.get('feed_protein', type=float),
            mortality=data.get('mortality', type=float),
            stock_count=data.get('stock_count', type=int),
            molting_status=data.get('molting_status', '').strip() or None,
            water_temperature=data.get('water_temperature', type=float),
            weather=data.get('weather', '').strip() or None,
            medication=data.get('medication', '').strip() or None,
            notes=data.get('notes', '').strip() or None,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '养殖日志已记录',
            'log': log.to_dict(),
        })

    return app


# 开发模式直接运行
if __name__ == '__main__':
    app = create_app()
    print('🦀 肴柒蟹 REST API 后端已启动')
    print(f'   📂 数据库: {app.config["SQLALCHEMY_DATABASE_URI"]}')
    print(f'   🌐 API 地址: http://0.0.0.0:5000')
    app.run(debug=True, host='0.0.0.0', port=5000)
