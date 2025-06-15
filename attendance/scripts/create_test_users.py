from django.contrib.auth.models import User
from attendance.models import Student, Teacher, Department, Major, LeaveRequest, AttendanceEvent
from django.utils import timezone
from datetime import timedelta
import random

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

    # 创建新的学生账号
    student2_user, _ = User.objects.get_or_create(username="student2")
    student2_user.set_password("testpass")
    student2_user.save()
    
    # 确保先删除已存在的 student2 记录（如果存在）
    Student.objects.filter(openid="student2").delete()
    
    # 创建新的 Student 记录
    student2 = Student.objects.create(
        stu_id="20230002",
        stu_name="张三",
        stu_sex=1,
        major=major,
        openid="student2"
    )

    # 创建超级管理员账号
    manage_user, created = User.objects.get_or_create(username='manage')
    if created or not manage_user.is_superuser:
        manage_user.set_password('manage123')
        manage_user.is_superuser = True
        manage_user.is_staff = True
        manage_user.save()
        print('超级管理员 manage 账号已创建/更新，密码: manage123')
    else:
        print('超级管理员 manage 账号已存在')

    print("测试用户创建完成！")

if __name__ == "__main__":
    fixed_count = 0
    for req in LeaveRequest.objects.all():
        event_date = req.event.event_date
        submit_date = req.submit_time.date()
        if submit_date >= event_date:
            # 随机提前1~3天
            days_before = random.randint(1, 3)
            new_submit_time = timezone.make_aware(timezone.datetime.combine(event_date, timezone.datetime.min.time())) - timedelta(days=days_before)
            req.submit_time = new_submit_time
            req.save()
            fixed_count += 1
    print(f"修正完成，共修正 {fixed_count} 条记录")

    for req in LeaveRequest.objects.all():
        if req.approval_status == 1:
            req.approver_notes = None
            req.save() 