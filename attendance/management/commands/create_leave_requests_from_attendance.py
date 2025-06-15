from django.core.management.base import BaseCommand
from attendance.models import Attendance, LeaveRequest, LEAVE_APPROVED
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = '为所有请假考勤自动生成或修正历史请假申请（LeaveRequest）'

    def handle(self, *args, **kwargs):
        REASONS = [
            '身体不适，需休息',
            '家中有事需请假',
            '参加竞赛，无法到课',
            '临时有急事',
            '外出办事',
            '个人原因',
        ]
        NOTES = [
            '同意请假，注意身体',
            '批准，按时补课',
            '已阅，注意安全',
            '同意，望早日康复',
            '批准，事后补交作业',
            '同意，注意课程进度',
        ]
        count = 0
        qs = Attendance.objects.filter(status=3)
        self.stdout.write(f'请假考勤记录数: {qs.count()}')
        for att in qs:
            event_date = att.event.event_date
            days_before = random.randint(1, 3)
            submit_time = timezone.make_aware(
                timezone.datetime.combine(event_date, timezone.datetime.min.time())
            ) - timedelta(days=days_before)
            reason = random.choice(REASONS)
            approver_notes = random.choice(NOTES)
            lr, created = LeaveRequest.objects.get_or_create(
                enrollment=att.enrollment,
                event=att.event,
                defaults={
                    'reason': reason,
                    'submit_time': submit_time,
                    'approval_status': LEAVE_APPROVED,
                    'approver_notes': approver_notes,
                }
            )
            if not created:
                lr.submit_time = submit_time
                lr.approver_notes = approver_notes
                lr.approval_status = LEAVE_APPROVED
                lr.save()
            count += 1
        self.stdout.write(self.style.SUCCESS(f'已生成或修正 {count} 条历史请假申请记录')) 