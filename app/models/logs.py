from datetime import datetime
from app.models import db

class SystemLog(db.Model):
    __tablename__ = 'system_log'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer)
    user_type = db.Column(db.String(20))  # 'super_user' or 'teacher'
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    
    @classmethod
    def log_action(cls, user_id, user_type, action, details=None, ip_address=None):
        """アクションをログに記録する"""
        log = cls(
            user_id=user_id,
            user_type=user_type,
            action=action,
            details=details,
            ip_address=ip_address
        )
        db.session.add(log)
        db.session.commit()
        return log