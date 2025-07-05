from datetime import datetime, timedelta
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
    
    @classmethod
    def delete_old_logs(cls, days=30):
        """指定した日数以上前のログを削除する"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 削除対象のログを取得
        old_logs = cls.query.filter(cls.timestamp < cutoff_date).all()
        deleted_count = len(old_logs)
        
        if deleted_count > 0:
            # 削除実行
            cls.query.filter(cls.timestamp < cutoff_date).delete()
            db.session.commit()
        
        return deleted_count