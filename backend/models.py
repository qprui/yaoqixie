"""
数据库模型定义
- User: 用户
- Pond: 养殖塘口
- EnvData: 环境监测数据
- FarmingLog: 养殖日志
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# =============================================
# 用户模型
# =============================================
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='farmer')
    # role: 'farmer' 养殖户, 'consumer' 消费者, 'expert' 专家
    real_name = db.Column(db.String(50), nullable=True)
    farm_address = db.Column(db.String(200), nullable=True)
    avatar_url = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)

    # 关联
    ponds = db.relationship('Pond', backref='owner', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


# =============================================
# 养殖塘口模型
# =============================================
class Pond(db.Model):
    __tablename__ = 'ponds'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False, comment='塘口名称')
    location = db.Column(db.String(200), nullable=True, comment='地理位置')
    area = db.Column(db.Float, nullable=True, comment='面积（亩）')
    species = db.Column(db.String(50), nullable=True, comment='养殖品种')
    stock_density = db.Column(db.Integer, nullable=True, comment='放养密度（只/亩）')
    water_depth = db.Column(db.Float, nullable=True, comment='水深（m）')
    aeration = db.Column(db.Boolean, default=False, comment='是否配备增氧机')
    notes = db.Column(db.Text, nullable=True, comment='备注')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # 关联
    env_data = db.relationship('EnvData', backref='pond', lazy='dynamic', cascade='all, delete-orphan')
    farming_logs = db.relationship('FarmingLog', backref='pond', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Pond {self.name}>'


# =============================================
# 环境监测数据模型
# =============================================
class EnvData(db.Model):
    __tablename__ = 'env_data'

    id = db.Column(db.Integer, primary_key=True)
    pond_id = db.Column(db.Integer, db.ForeignKey('ponds.id'), nullable=False, index=True)
    temperature = db.Column(db.Float, nullable=True, comment='水温(°C)')
    dissolved_oxygen = db.Column(db.Float, nullable=True, comment='溶解氧(mg/L)')
    ph_value = db.Column(db.Float, nullable=True, comment='pH值')
    ammonia = db.Column(db.Float, nullable=True, comment='氨氮(mg/L)')
    salinity = db.Column(db.Float, nullable=True, comment='盐度(‰)')
    turbidity = db.Column(db.Float, nullable=True, comment='浊度(NTU)')
    recorded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), comment='记录时间')
    source = db.Column(db.String(20), default='manual', comment='数据来源: manual/IoT')

    def to_dict(self):
        return {
            'id': self.id,
            'pond_id': self.pond_id,
            'temperature': self.temperature,
            'dissolved_oxygen': self.dissolved_oxygen,
            'ph_value': self.ph_value,
            'ammonia': self.ammonia,
            'salinity': self.salinity,
            'turbidity': self.turbidity,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'source': self.source,
        }

    def __repr__(self):
        return f'<EnvData pond={self.pond_id} at {self.recorded_at}>'


# =============================================
# 养殖日志模型
# =============================================
class FarmingLog(db.Model):
    __tablename__ = 'farming_logs'

    id = db.Column(db.Integer, primary_key=True)
    pond_id = db.Column(db.Integer, db.ForeignKey('ponds.id'), nullable=False, index=True)
    log_date = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date(), comment='记录日期')
    feeding_amount = db.Column(db.Float, nullable=True, comment='投喂量(kg)')
    feed_protein = db.Column(db.Float, nullable=True, comment='饲料蛋白比(%)')
    mortality = db.Column(db.Float, nullable=True, comment='死亡率(%)')
    stock_count = db.Column(db.Integer, nullable=True, comment='存塘量(只)')
    molting_status = db.Column(db.String(20), nullable=True, comment='蜕壳情况')
    water_temperature = db.Column(db.Float, nullable=True, comment='当日水温(°C)')
    weather = db.Column(db.String(50), nullable=True, comment='天气情况')
    medication = db.Column(db.String(200), nullable=True, comment='用药记录')
    notes = db.Column(db.Text, nullable=True, comment='备注')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'pond_id': self.pond_id,
            'log_date': self.log_date.isoformat() if self.log_date else None,
            'feeding_amount': self.feeding_amount,
            'feed_protein': self.feed_protein,
            'mortality': self.mortality,
            'stock_count': self.stock_count,
            'molting_status': self.molting_status,
            'water_temperature': self.water_temperature,
            'weather': self.weather,
            'medication': self.medication,
            'notes': self.notes,
        }

    def __repr__(self):
        return f'<FarmingLog pond={self.pond_id} date={self.log_date}>'
