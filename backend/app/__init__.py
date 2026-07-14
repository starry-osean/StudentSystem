"""
Flask 应用工厂模块
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.students import students_bp
    from app.routes.courses import courses_bp
    from app.routes.scores import scores_bp
    from app.routes.analysis import analysis_bp
    from app.routes.predictions import predictions_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(courses_bp, url_prefix='/api/courses')
    app.register_blueprint(scores_bp, url_prefix='/api/scores')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(predictions_bp, url_prefix='/api/predictions')

    # 健康检查路由
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'API 服务运行正常'}

    return app
