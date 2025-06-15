from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from attendance.models import Student, Department, Major, Course, Enrollment
from django.utils import timezone

class Command(BaseCommand):
    help = '创建示例学生数据'

    def handle(self, *args, **kwargs):
        # 创建院系和专业（不指定主键，使用默认自增）
        dept, _ = Department.objects.get_or_create(
            dept_name='计算机科学与技术学院'
        )
        
        major, _ = Major.objects.get_or_create(
            major_name='计算机科学与技术',
            defaults={
                'dept': dept
            }
        )

        # 创建示例学生
        students_data = [
            {'stu_id': '2023003', 'stu_name': 'student3'},
            {'stu_id': '2023004', 'stu_name': 'student4'},
            {'stu_id': '2023005', 'stu_name': 'student5'},
            {'stu_id': '2023006', 'stu_name': 'student6'},
            {'stu_id': '2023007', 'stu_name': 'student7'},
            {'stu_id': '2023008', 'stu_name': 'student8'},
        ]

        for data in students_data:
            # 创建用户账号
            user, created = User.objects.get_or_create(
                username=data['stu_id'],
                defaults={
                    'password': 'pbkdf2_sha256$600000$testpass',
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f"创建用户: {data['stu_id']}")
            
            # 创建学生信息
            student, created = Student.objects.get_or_create(
                stu_id=data['stu_id'],
                defaults={
                    'stu_name': data['stu_name'],
                    'major': major,
                    'openid': data['stu_id'],
                    'stu_sex': 1
                }
            )
            
            if created:
                self.stdout.write(f"创建学生: {data['stu_name']}")

        # 创建Python程序设计课程（如不存在）
        course, _ = Course.objects.get_or_create(
            course_id='C001',
            defaults={
                'course_name': 'Python程序设计',
                'dept': dept,
                'credit': 3,
                'hours': 48
            }
        )
        
        for data in students_data:
            student = Student.objects.get(stu_id=data['stu_id'])
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=course,
                semester='202401'
            )
            
            if created:
                self.stdout.write(f"添加选课记录: {data['stu_name']} -> {course.course_name}")

        self.stdout.write(self.style.SUCCESS('成功创建示例学生数据')) 