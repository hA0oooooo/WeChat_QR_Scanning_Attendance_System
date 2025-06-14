from django.contrib.auth.models import User
from attendance.models import Student, Teacher, Department, Major

def run():
    # 创建院系和专业
    dept, _ = Department.objects.get_or_create(dept_name="测试院系")
    major, _ = Major.objects.get_or_create(major_name="测试专业", dept=dept)

    # 创建学生账号
    student_user, _ = User.objects.get_or_create(username="student_test")
    student_user.set_password("123456")
    student_user.save()
    Student.objects.get_or_create(stu_id="student_test", stu_name="测试学生", stu_sex=1, major=major, openid="student_test")

    # 创建教师账号
    teacher_user, _ = User.objects.get_or_create(username="teacher_test")
    teacher_user.set_password("123456")
    teacher_user.save()
    Teacher.objects.get_or_create(teacher_id="teacher_test", teacher_name="测试教师", dept=dept)

    # 创建管理员账号
    admin_user, _ = User.objects.get_or_create(username="admin_test", is_superuser=True, is_staff=True)
    admin_user.set_password("123456")
    admin_user.save()

    print("测试用户创建完成！") 