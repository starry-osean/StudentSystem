"""
成绩模型
"""
from datetime import datetime
from app import db

class Score(db.Model):
    """成绩模型"""
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    score = db.Column(db.Float)  # 分数
    grade = db.Column(db.String(5))  # 等级: A, B, C, D, E
    semester = db.Column(db.String(20))  # 学期
    exam_type = db.Column(db.String(20), default='regular')  # regular(平时), midterm(期中), final(期末)
    remarks = db.Column(db.Text)  # 备注
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 联合唯一约束
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', 'semester', name='uq_student_course_semester'),
    )

    @staticmethod
    def calculate_grade(score):
        """根据分数计算等级"""
        if score is None:
            return None
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'E'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'student_name': self.student.name if self.student else None,
            'student_no': self.student.student_no if self.student else None,
            'course_name': self.course.name if self.course else None,
            'course_no': self.course.course_no if self.course else None,
            'score': self.score,
            'grade': self.grade or self.calculate_grade(self.score),
            'semester': self.semester,
            'exam_type': self.exam_type,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Score {self.student_id}-{self.course_id}: {self.score}>'
