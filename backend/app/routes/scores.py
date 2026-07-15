"""
成绩管理路由模块
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import Score, Student, Course
from app.utils import token_required

scores_bp = Blueprint('scores', __name__)

@scores_bp.route('', methods=['GET'])
@token_required
def get_scores():
    """获取成绩列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    student_id = request.args.get('student_id', type=int)
    course_id = request.args.get('course_id', type=int)
    semester = request.args.get('semester', '')
    search = request.args.get('search', '')

    query = Score.query

    if student_id:
        query = query.filter(Score.student_id == student_id)
    if course_id:
        query = query.filter(Score.course_id == course_id)
    if semester:
        query = query.filter(Score.semester == semester)
    if search:
        query = query.join(Student).join(Course).filter(
            db.or_(
                Student.name.like(f'%{search}%'),
                Student.student_no.like(f'%{search}%'),
                Course.name.like(f'%{search}%')
            )
        )

    query = query.order_by(Score.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'list': [s.to_dict() for s in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'pages': pagination.pages
        }
    })

@scores_bp.route('/<int:score_id>', methods=['GET'])
@token_required
def get_score(score_id):
    """获取成绩详情"""
    score = Score.query.get(score_id)
    if not score:
        return jsonify({'code': 404, 'message': '成绩记录不存在'}), 404

    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': score.to_dict()
    })

@scores_bp.route('', methods=['POST'])
@token_required
def create_score():
    """录入成绩"""
    data = request.get_json()

    if not data:
        return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400

    if not data.get('student_id') or not data.get('course_id'):
        return jsonify({'code': 400, 'message': '学生ID和课程ID不能为空'}), 400

    # 验证学生存在
    student = Student.query.get(data['student_id'])
    if not student:
        return jsonify({'code': 404, 'message': '学生不存在'}), 404

    # 验证课程存在
    course = Course.query.get(data['course_id'])
    if not course:
        return jsonify({'code': 404, 'message': '课程不存在'}), 404

    # 检查是否已有该成绩记录
    existing = Score.query.filter_by(
        student_id=data['student_id'],
        course_id=data['course_id'],
        semester=data.get('semester', '')
    ).first()
    if existing:
        return jsonify({'code': 400, 'message': '该成绩记录已存在'}), 400

    try:
        score_value = data.get('score')
        grade = Score.calculate_grade(score_value)

        score = Score(
            student_id=data['student_id'],
            course_id=data['course_id'],
            score=score_value,
            grade=grade,
            semester=data.get('semester', ''),
            exam_type=data.get('exam_type', 'regular'),
            remarks=data.get('remarks')
        )

        db.session.add(score)
        db.session.commit()

        return jsonify({
            'code': 201,
            'message': '录入成功',
            'data': score.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'录入失败: {str(e)}'}), 500

@scores_bp.route('/<int:score_id>', methods=['PUT'])
@token_required
def update_score(score_id):
    """更新成绩"""
    score = Score.query.get(score_id)
    if not score:
        return jsonify({'code': 404, 'message': '成绩记录不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400

    try:
        if 'score' in data:
            score.score = data['score']
            score.grade = Score.calculate_grade(data['score'])
        if 'semester' in data:
            score.semester = data['semester']
        if 'exam_type' in data:
            score.exam_type = data['exam_type']
        if 'remarks' in data:
            score.remarks = data['remarks']

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': score.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500

@scores_bp.route('/<int:score_id>', methods=['DELETE'])
@token_required
def delete_score(score_id):
    """删除成绩"""
    score = Score.query.get(score_id)
    if not score:
        return jsonify({'code': 404, 'message': '成绩记录不存在'}), 404

    try:
        db.session.delete(score)
        db.session.commit()
        return jsonify({'code': 200, 'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'}), 500

@scores_bp.route('/student/<int:student_id>', methods=['GET'])
@token_required
def get_student_scores(student_id):
    """获取单个学生的所有成绩"""
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'code': 404, 'message': '学生不存在'}), 404

    scores = Score.query.filter_by(student_id=student_id).order_by(Score.semester).all()

    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': [s.to_dict() for s in scores]
    })

@scores_bp.route('/course/<int:course_id>', methods=['GET'])
@token_required
def get_course_scores(course_id):
    """获取课程的所有成绩"""
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'code': 404, 'message': '课程不存在'}), 404

    scores = Score.query.filter_by(course_id=course_id).order_by(Score.score.desc()).all()

    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': [s.to_dict() for s in scores]
    })
