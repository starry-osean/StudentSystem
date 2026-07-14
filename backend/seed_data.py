"""
测试数据生成脚本
"""
import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Student, Course, Score

# 省份列表
PROVINCES = [
    '北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江',
    '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南',
    '湖北', '湖南', '广东', '广西', '海南', '重庆', '四川', '贵州',
    '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆'
]

# 专业列表
MAJORS = ['计算机科学与技术', '软件工程', '网络工程', '信息安全', '数据科学', '人工智能']

# 班级列表
CLASSES = ['1班', '2班', '3班', '4班']

# 教师列表
TEACHERS = ['张教授', '李教授', '王副教授', '刘讲师', '陈讲师', '周讲师']


def generate_students(count=1000):
    """生成学生数据"""
    students = []
    start_no = 2024001

    for i in range(count):
        student_no = str(start_no + i)
        major = random.choice(MAJORS)
        class_name = random.choice(CLASSES)

        # 生成随机出生日期
        birth_year = random.randint(2002, 2006)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        birth_date = datetime(birth_year, birth_month, birth_day).date()

        # 生成联系方式
        phone = f'138{random.randint(10000000, 99999999)}'
        email = f's{student_no}@student.edu.cn'

        student = Student(
            student_no=student_no,
            name=f'学生{i+1:04d}',
            gender=random.choice(['male', 'female']),
            birth_date=birth_date,
            phone=phone,
            email=email,
            major=major,
            class_name=f'{major[:2]}{class_name}',
            origin_province=random.choice(PROVINCES),
            address=f'学生宿舍{i % 10 + 1}号楼{random.randint(101, 999)}室',
            status='active'
        )
        students.append(student)

    return students


def generate_courses():
    """生成课程数据"""
    course_data = [
        ('CS101', '高等数学', 4.0, 64, 'compulsory'),
        ('CS102', '线性代数', 3.0, 48, 'compulsory'),
        ('CS103', '概率论与数理统计', 3.0, 48, 'compulsory'),
        ('CS104', '大学物理', 3.0, 48, 'compulsory'),
        ('CS201', '数据结构', 4.0, 64, 'compulsory'),
        ('CS202', '算法设计', 3.0, 48, 'compulsory'),
        ('CS203', '操作系统', 3.0, 48, 'compulsory'),
        ('CS204', '计算机网络', 3.0, 48, 'compulsory'),
        ('CS301', '数据库原理', 3.0, 48, 'compulsory'),
        ('CS302', '软件工程', 2.0, 32, 'compulsory'),
    ]

    semesters = ['2024-1', '2024-2', '2025-1']
    departments = ['计算机学院', '软件学院', '信息学院']

    courses = []
    for i, (course_no, name, credits, hours, course_type) in enumerate(course_data):
        course = Course(
            course_no=course_no,
            name=name,
            credits=credits,
            hours=hours,
            teacher=random.choice(TEACHERS),
            semester=random.choice(semesters),
            department=random.choice(departments),
            course_type=course_type,
            description=f'{name}是{model_type_desc(course_type)}',
            max_students=100,
            status='active'
        )
        courses.append(course)

    return courses


def model_type_desc(course_type):
    """课程类型描述"""
    return '必修课' if course_type == 'compulsory' else '选修课'


def generate_scores(students, courses):
    """生成成绩数据"""
    scores = []
    semesters = ['2024-1', '2024-2', '2025-1']

    for student in students:
        # 每个学生选修 3-8 门课程
        selected_courses = random.sample(courses, random.randint(3, min(8, len(courses))))

        for course in selected_courses:
            semester = random.choice(semesters)

            # 正态分布生成成绩，均值75，标准差15
            score = random.gauss(75, 15)
            score = max(0, min(100, round(score, 1)))

            s = Score(
                student_id=student.id,
                course_id=course.id,
                score=score,
                grade=Score.calculate_grade(score),
                semester=semester,
                exam_type='final',
                remarks=''
            )
            scores.append(s)

    return scores


def seed_data(student_count=1000):
    """执行数据填充"""
    app = create_app()
    with app.app_context():
        print('开始生成测试数据...')

        # 检查是否已有数据
        if Student.query.count() > 0:
            print('数据库中已有数据，跳过生成')
            return

        # 生成课程
        print('生成课程数据...')
        courses = generate_courses()
        db.session.add_all(courses)
        db.session.commit()
        print(f'已生成 {len(courses)} 门课程')

        # 生成学生
        print('生成学生数据...')
        students = generate_students(student_count)
        db.session.add_all(students)
        db.session.commit()
        print(f'已生成 {len(students)} 名学生')

        # 刷新会话以获取学生ID
        db.session.expire_all()
        students = Student.query.all()
        courses = Course.query.all()

        # 生成成绩
        print('生成成绩数据...')
        scores = generate_scores(students, courses)
        db.session.add_all(scores)
        db.session.commit()
        print(f'已生成 {len(scores)} 条成绩记录')

        print('数据生成完成！')


if __name__ == '__main__':
    import sys
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    seed_data(count)
