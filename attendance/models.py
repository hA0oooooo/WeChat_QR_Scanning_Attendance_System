from django.db import models
from django.utils import timezone

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
    stu_id = models.CharField(max_length=11, primary_key=True, verbose_name='学号')
    stu_name = models.CharField(max_length=50, verbose_name='姓名')
    stu_sex = models.CharField(max_length=1, choices=[('0', '男'), ('1', '女')], verbose_name='性别')
    major = models.ForeignKey(Major, on_delete=models.SET_NULL, null=True, db_column='major_id', verbose_name='专业')
    openid = models.CharField(max_length=50, unique=True, verbose_name='微信openid')

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
    scan_start_time = models.TimeField(verbose_name='扫码开始时间')
    scan_end_time = models.TimeField(verbose_name='扫码结束时间')
    event_status = models.CharField(max_length=1, choices=[('0', '有效'), ('1', '无效')], 
                                  default='0', verbose_name='事件状态')
    creation_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '考勤事件'
        verbose_name_plural = verbose_name
        db_table = 'AttendanceEvent'

    def __str__(self):
        return f"{self.course.course_name}-{self.event_date}"

class Attendance(models.Model):
    """考勤记录表"""
    attend_id = models.PositiveIntegerField(primary_key=True, auto_created=True, verbose_name='考勤记录ID')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, db_column='enroll_id', verbose_name='选课记录')
    event = models.ForeignKey(AttendanceEvent, on_delete=models.CASCADE, db_column='event_id', verbose_name='考勤事件')
    scan_time = models.DateTimeField(null=True, blank=True, verbose_name='扫码时间')
    status = models.CharField(max_length=1, choices=[('0', '出勤'), ('1', '缺勤'), ('2', '请假')], 
                            verbose_name='考勤状态')
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
    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='提交时间')
    approval_status = models.CharField(max_length=1, 
                                     choices=[('0', '待审批'), ('1', '已批准'), ('2', '已驳回')],
                                     default='0', verbose_name='审批状态')
    approver = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, db_column='approver_teacher_id', 
                               verbose_name='审批教师')
    approval_time = models.DateTimeField(null=True, blank=True, verbose_name='审批时间')
    approver_notes = models.TextField(null=True, blank=True, verbose_name='审批备注')

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