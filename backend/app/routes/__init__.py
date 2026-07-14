"""
路由模块
"""
from app.routes.auth import auth_bp
from app.routes.students import students_bp
from app.routes.courses import courses_bp
from app.routes.scores import scores_bp
from app.routes.analysis import analysis_bp
from app.routes.predictions import predictions_bp

__all__ = ['auth_bp', 'students_bp', 'courses_bp', 'scores_bp', 'analysis_bp', 'predictions_bp']
