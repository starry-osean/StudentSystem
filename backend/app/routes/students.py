"""
学生管理路由模块
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import Student
from app.utils import token_required

students_bp = Blueprint('students', __name__)

@students_bp.route('', methods=['GET'])
@token_required
def get_students():
    """获取学生列表（支持分页和筛选）"""
    # 分页参数
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    # 筛选参数
    search = request.args.get('search', '')
    major = request.args.get('major', '')
    class_name = request.args.get('class_name', '')
    status = request.args.get('status', '')

    # 构建查询
    query = Student.query

    if search:
        query = query.filter(
            db.or_(
                Student.name.like(f'%{search}%'),
                Student.student_no.like(f'%{search}%'),
                Student.email.like(f'%{search}%')
            )
        )
    if major:
        query = query.filter(Student.major == major)
    if class_name:
        query = query.filter(Student.class_name == class_name)
    if status:
        query = query.filter(Student.status == status)

    # 排序和分页
    query = query.order_by(Student.created_at.desc())
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

@students_bp.route('/<int:student_id>', methods=['GET'])
@token_required
def get_student(student_id):
    """获取学生详情"""
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'code': 404, 'message': '学生不存在'}), 404

    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': student.to_dict()
    })

@students_bp.route('', methods=['POST'])
@token_required
def create_student():
    """创建学生"""
    data = request.get_json()

    if not data:
        return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400

    # 验证必填字段
    if not data.get('student_no') or not data.get('name'):
        return jsonify({'code': 400, 'message': '学号和姓名不能为空'}), 400

    # 检查学号是否已存在
    if Student.query.filter_by(student_no=data['student_no']).first():
        return jsonify({'code': 400, 'message': '学号已存在'}), 400

    try:
        student = Student(
            student_no=data['student_no'],
            name=data['name'],
            gender=data.get('gender'),
            birth_date=data.get('birth_date'),
            phone=data.get('phone'),
            email=data.get('email'),
            major=data.get('major'),
            class_name=data.get('class_name'),
            origin_province=data.get('origin_province'),
            address=data.get('address'),
            status=data.get('status', 'active')
        )

        db.session.add(student)
        db.session.commit()

        return jsonify({
            'code': 201,
            'message': '创建成功',
            'data': student.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'创建失败: {str(e)}'}), 500

@students_bp.route('/<int:student_id>', methods=['PUT'])
@token_required
def update_student(student_id):
    """更新学生信息"""
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'code': 404, 'message': '学生不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400

    # 检查学号是否被其他学生使用
    if data.get('student_no') and data['student_no'] != student.student_no:
        existing = Student.query.filter_by(student_no=data['student_no']).first()
        if existing:
            return jsonify({'code': 400, 'message': '学号已被其他学生使用'}), 400

    try:
        # 更新字段
        updatable_fields = [
            'student_no', 'name', 'gender', 'birth_date', 'phone',
            'email', 'major', 'class_name', 'origin_province',
            'address', 'status'
        ]
        for field in updatable_fields:
            if field in data:
                setattr(student, field, data[field])

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': student.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500

@students_bp.route('/<int:student_id>', methods=['DELETE'])
@token_required
def delete_student(student_id):
    """删除学生"""
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'code': 404, 'message': '学生不存在'}), 404

    try:
        db.session.delete(student)
        db.session.commit()
        return jsonify({'code': 200, 'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'}), 500
