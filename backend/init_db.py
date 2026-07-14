"""
数据库初始化和创建脚本
"""
from app import create_app, db
from app.models import User, Student, Course, Score

def init_db():
    """初始化数据库"""
    app = create_app()
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库表创建成功！")

        # 创建默认管理员账户
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("默认管理员账户已创建: admin / admin123")
        else:
            print("管理员账户已存在")

if __name__ == '__main__':
    init_db()
