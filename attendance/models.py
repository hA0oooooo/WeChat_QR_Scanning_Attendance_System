from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Department(models.Model):
    """院系信息表"""
    dept_id = models.PositiveSmallIntegerField(primary_key=True, auto_created=True, verbose_name='院系ID')
    dept_name = models.CharField(max_length=50, unique=True, verbose_name='院系名')

    class Meta:
        verbose_name = '院系'
        verbose_name_plural = verbose_name
        db_table = 'Department'

    def __str__(self):
        return self.dept_name

class Major(models.Model):
    """专业信息表"""
    major_id = models.PositiveSmallIntegerField(primary_key=True, auto_created=True, verbose_name='专业ID')
    major_name = models.CharField(max_length=50, unique=True, verbose_name='专业名')
    dept = models.ForeignKey(Department, on_delete=models.RESTRICT, db_column='dept_id', verbose_name='所属院系')

    class Meta:
        verbose_name = '专业'
        verbose_name_plural = verbose_name
        db_table = 'Major'

    def __str__(self):
        return self.major_name

class Student(models.Model):
    """学生信息表"""
    stu_id = models.CharField(max_length=20, primary_key=True, verbose_name='学号')
    stu_name = models.CharField(max_length=50, verbose_name='姓名')
    GENDER_MALE = 1    # 男
    GENDER_FEMALE = 2  # 女
    
    GENDER_CHOICES = [
        (GENDER_MALE, '男'),
        (GENDER_FEMALE, '女'),
    ]
    
    stu_sex = models.IntegerField(choices=GENDER_CHOICES, null=False, verbose_name='性别')
    major = models.ForeignKey(Major, on_delete=models.SET_NULL, null=True, db_column='major_id', verbose_name='专业')
    openid = models.CharField(max_length=50, unique=True, verbose_name='微信openid')
    stu_class = models.CharField(max_length=50, verbose_name='班级')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '学生'
        verbose_name_plural = verbose_name
        db_table = 'Student'

    def __str__(self):
        return f"{self.stu_name}({self.stu_id})"

class Course(models.Model):
    """课程信息表"""
    course_id = models.CharField(max_length=12, primary_key=True, verbose_name='课程代码')
    course_name = models.CharField(max_length=50, verbose_name='课程名称')
    dept = models.ForeignKey(Department, on_delete=models.RESTRICT, db_column='dept_id', verbose_name='开课院系')

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = verbose_name
        db_table = 'Course'

    def __str__(self):
        return f"{self.course_name}({self.course_id})"

class Teacher(models.Model):
    """教师信息表"""
    teacher_id = models.CharField(max_length=5, primary_key=True, verbose_name='教师工号')
    teacher_name = models.CharField(max_length=50, verbose_name='教师姓名')
    dept = models.ForeignKey(Department, on_delete=models.RESTRICT, db_column='dept_id', verbose_name='所属院系')

    class Meta:
        verbose_name = '教师'
        verbose_name_plural = verbose_name
        db_table = 'Teacher'

    def __str__(self):
        return f"{self.teacher_name}({self.teacher_id})"

class Enrollment(models.Model):
    """选课记录表"""
    enroll_id = models.PositiveIntegerField(primary_key=True, auto_created=True, verbose_name='选课记录ID')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='stu_id', verbose_name='学生')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id', verbose_name='课程')
    semester = models.CharField(max_length=6, verbose_name='学期')

    class Meta:
        verbose_name = '选课记录'
        verbose_name_plural = verbose_name
        db_table = 'Enrollment'
        unique_together = ['student', 'course', 'semester']

    def __str__(self):
        return f"{self.student.stu_name}-{self.course.course_name}"

class AttendanceEvent(models.Model):
    """考勤事件表"""
    event_id = models.PositiveIntegerField(primary_key=True, auto_created=True, verbose_name='考勤事件ID')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id', verbose_name='课程')
    event_date = models.DateField(verbose_name='事件日期')
    scan_start_time = models.TimeField(verbose_name='扫码有效开始时间')
    scan_end_time = models.TimeField(verbose_name='扫码有效结束时间')
    event_status = models.IntegerField(choices=EVENT_STATUS_CHOICES, null=False, default=EVENT_VALID, verbose_name='事件状态')

    class Meta:
        verbose_name = '考勤事件'
        verbose_name_plural = verbose_name
        db_table = 'AttendanceEvent'

    def __str__(self):
        return f"{self.course.course_name}-{self.event_date} {self.scan_start_time}"

class Attendance(models.Model):
    """考勤记录表"""
    attend_id = models.PositiveIntegerField(primary_key=True, auto_created=True, verbose_name='考勤记录ID')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, db_column='enroll_id', verbose_name='选课记录')
    event = models.ForeignKey(AttendanceEvent, on_delete=models.CASCADE, db_column='event_id', verbose_name='考勤事件')
    status = models.IntegerField(choices=STATUS_CHOICES, null=False, verbose_name='考勤状态')
    scan_time = models.DateTimeField(null=True, blank=True, verbose_name='扫码时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    notes = models.TextField(null=True, blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '考勤记录'
        verbose_name_plural = verbose_name
        db_table = 'Attendance'
        unique_together = ['enrollment', 'event']

    def __str__(self):
        return f"{self.enrollment.student.stu_name}-{self.event.course.course_name}"

class LeaveRequest(models.Model):
    """请假申请表"""
    leave_request_id = models.PositiveIntegerField(primary_key=True, auto_created=True, verbose_name='请假申请ID')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, db_column='enroll_id', verbose_name='选课记录')
    event = models.ForeignKey(AttendanceEvent, on_delete=models.CASCADE, db_column='event_id', verbose_name='考勤事件')
    reason = models.TextField(verbose_name='请假原因')
    approval_status = models.IntegerField(choices=LEAVE_STATUS_CHOICES, null=False, verbose_name='审批状态')
    approver = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, db_column='approver_teacher_id', 
                               verbose_name='审批教师')
    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='提交时间')
    approval_time = models.DateTimeField(null=True, blank=True, verbose_name='审批时间')
    approver_notes = models.TextField(null=True, blank=True, verbose_name='审批备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '请假申请'
        verbose_name_plural = verbose_name
        db_table = 'LeaveRequest'
        unique_together = ['enrollment', 'event']

    def __str__(self):
        return f"{self.enrollment.student.stu_name}-{self.event.course.course_name}"

class TeachingAssignment(models.Model):
    """教学安排表"""
    assignment_id = models.PositiveIntegerField(primary_key=True, auto_created=True, verbose_name='教学安排ID')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, db_column='teacher_id', verbose_name='教师')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id', verbose_name='课程')

    class Meta:
        verbose_name = '教学安排'
        verbose_name_plural = verbose_name
        db_table = 'TeachingAssignment'
        unique_together = ['teacher', 'course']

    def __str__(self):
        return f"{self.teacher.teacher_name}-{self.course.course_name}"

class ClassSchedule(models.Model):
    """课程时间安排表"""
    schedule_id = models.PositiveIntegerField(primary_key=True, auto_created=True, verbose_name='时间安排ID')
    assignment = models.ForeignKey(TeachingAssignment, on_delete=models.CASCADE, db_column='assignment_id', 
                                 verbose_name='教学安排')
    weekday = models.PositiveSmallIntegerField(choices=[(i, f'星期{i}') for i in range(1, 8)], verbose_name='星期')
    start_period = models.PositiveSmallIntegerField(verbose_name='开始节次')
    end_period = models.PositiveSmallIntegerField(verbose_name='结束节次')
    location = models.CharField(max_length=50, verbose_name='上课地点')

    class Meta:
        verbose_name = '课程时间安排'
        verbose_name_plural = verbose_name
        db_table = 'ClassSchedule'

    def __str__(self):
        return f"{self.assignment.course.course_name}-{self.get_weekday_display()}"

class SystemSettings(models.Model):
    """系统设置模型"""
    system_name = models.CharField('系统名称', max_length=100, default='微信扫码考勤系统')
    attendance_start_time = models.TimeField('默认考勤开始时间', default='08:00')
    attendance_end_time = models.TimeField('默认考勤结束时间', default='17:00')
    late_threshold = models.IntegerField('迟到阈值（分钟）', default=15)
    early_leave_threshold = models.IntegerField('早退阈值（分钟）', default=15)
    max_leave_days = models.IntegerField('最大请假天数', default=30)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '系统设置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.system_name

class PermissionSettings(models.Model):
    """权限设置模型"""
    student_view_attendance = models.BooleanField('学生查看考勤记录', default=True)
    student_apply_leave = models.BooleanField('学生申请请假', default=True)
    teacher_create_attendance = models.BooleanField('教师创建考勤', default=True)
    teacher_approve_leave = models.BooleanField('教师审批请假', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '权限设置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '权限设置'

class SystemLog(models.Model):
    """系统日志模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    action = models.CharField('操作', max_length=200)
    ip_address = models.GenericIPAddressField('IP地址')
    status = models.BooleanField('状态', default=True)  # True表示成功，False表示失败
    timestamp = models.DateTimeField('时间', auto_now_add=True)

    class Meta:
        verbose_name = '系统日志'
        verbose_name_plural = verbose_name
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.user.username} - {self.action} - {self.timestamp}' 