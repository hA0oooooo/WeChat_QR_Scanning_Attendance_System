import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from attendance.models import Course, Student, Enrollment, AttendanceEvent, Attendance, STATUS_PRESENT, STATUS_ABSENT, STATUS_LEAVE, LeaveRequest
from datetime import timedelta

class Command(BaseCommand):
    help = '为C001课程所有学生生成7周考勤事件和随机考勤记录'

    def handle(self, *args, **kwargs):
        course = Course.objects.get(course_id='C001')
        students = Student.objects.filter(enrollment__course=course).distinct()
        enrollments = Enrollment.objects.filter(course=course)

        # 彻底清空所有考勤事件和考勤记录
        Attendance.objects.all().delete()
        AttendanceEvent.objects.all().delete()

        today = timezone.now().date()
        # 生成7周的考勤事件（每周一）
        events = []
        for i in range(7):
            event_date = today - timedelta(days=today.weekday()) - timedelta(weeks=6-i)
            event = AttendanceEvent.objects.create(
                course=course,
                event_date=event_date,
                scan_start_time=timezone.datetime.strptime('08:00:00', '%H:%M:%S').time(),
                scan_end_time=timezone.datetime.strptime('09:00:00', '%H:%M:%S').time(),
                event_status=1
            )
            events.append(event)
        self.stdout.write(self.style.SUCCESS(f'已生成7次考勤事件'))

        # 为每个学生每次考勤生成考勤记录
        for enrollment in enrollments:
            for event in events:
                status = random.choices(
                    [STATUS_PRESENT, STATUS_ABSENT, STATUS_LEAVE],
                    weights=[0.7, 0.2, 0.1]
                )[0]
                scan_time = None
                if status == STATUS_PRESENT:
                    start_dt = timezone.datetime.combine(event.event_date, event.scan_start_time)
                    end_dt = timezone.datetime.combine(event.event_date, event.scan_end_time)
                    delta_seconds = int((end_dt - start_dt).total_seconds())
                    random_seconds = random.randint(0, max(0, delta_seconds))
                    scan_time = timezone.make_aware(start_dt + timedelta(seconds=random_seconds))
                Attendance.objects.create(
                    enrollment=enrollment,
                    event=event,
                    scan_time=scan_time,
                    status=status
                )
        self.stdout.write(self.style.SUCCESS('已为所有学生生成7周考勤记录'))

        # 生成请假申请测试数据
        leave_event = AttendanceEvent.objects.filter(event_date=events[-1].event_date).first()  # 最后一周（6月22日）
        leave_students = list(students)[:4]  # 任选4个学生
        leave_reasons = [
            "家中有事需请假",
            "身体不适，需休息",
            "参加竞赛，无法到课",
            "临时有急事"
        ]
        leave_statuses = [1, 1, 2, 3]  # approval_status: 1待审批, 2已通过, 3已驳回
        for stu, reason, status in zip(leave_students, leave_reasons, leave_statuses):
            enrollment = Enrollment.objects.filter(student=stu, course=leave_event.course).first()
            LeaveRequest.objects.create(
                enrollment=enrollment,
                event=leave_event,
                reason=reason,
                approval_status=status
            ) 