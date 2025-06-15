from django.core.management.base import BaseCommand
from attendance.models import Course, Student, Enrollment, AttendanceEvent, LeaveRequest, LEAVE_PENDING
from django.utils import timezone
from datetime import timedelta, date, time
import random

class Command(BaseCommand):
    help = '为所有选课学生在6月23日生成待审批请假申请'

    def handle(self, *args, **kwargs):
        REASONS = [
            '家中有事需请假',
            '身体不适，需休息',
            '参加竞赛，无法到课',
            '临时有急事',
            '外出办事',
            '个人原因',
        ]
        NOTES = [
            '请老师批准，谢谢',
            '望老师理解',
            '如有需要可补交作业',
            '请假后会及时补课',
            '感谢老师支持',
        ]
        # 1. 获取课程
        course = Course.objects.filter(course_name__contains='Python').first()
        if not course:
            self.stdout.write(self.style.ERROR('未找到Python相关课程'))
            return
        # 2. 确保6月23日有考勤事件
        event_date = date(2025, 6, 23)
        event, created = AttendanceEvent.objects.get_or_create(
            course=course,
            event_date=event_date,
            defaults={
                'scan_start_time': time(8, 0),
                'scan_end_time': time(9, 0),
                'event_status': 1
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('已创建6月23日考勤事件'))
        # 3. 为所有选课学生生成待审批请假申请
        enrollments = Enrollment.objects.filter(course=course)
        count = 0
        for enrollment in enrollments:
            # 检查是否已存在该事件的请假申请
            exists = LeaveRequest.objects.filter(enrollment=enrollment, event=event, approval_status=1).exists()
            if not exists:
                days_before = random.randint(1, 3)
                submit_time = timezone.make_aware(
                    timezone.datetime.combine(event_date, timezone.datetime.min.time())
                ) - timedelta(days=days_before)
                reason = random.choice(REASONS)
                LeaveRequest.objects.create(
                    enrollment=enrollment,
                    event=event,
                    reason=reason,
                    submit_time=submit_time,
                    approval_status=LEAVE_PENDING,
                    approver_notes=None,
                )
                count += 1
        self.stdout.write(self.style.SUCCESS(f'已为{count}名学生生成待审批请假申请')) 