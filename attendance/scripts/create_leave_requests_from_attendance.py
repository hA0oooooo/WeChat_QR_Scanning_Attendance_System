from attendance.models import Attendance, LeaveRequest, LEAVE_APPROVED
from django.utils import timezone
from datetime import timedelta
import random

def run():
    REASONS = [
        '身体不适，需休息',
        '家中有事需请假',
        '参加竞赛，无法到课',
        '临时有急事',
        '外出办事',
        '个人原因',
    ]
    count = 0
    qs = Attendance.objects.filter(status=3)
    print('请假考勤记录数:', qs.count())
    for att in qs:
        exists = LeaveRequest.objects.filter(enrollment=att.enrollment, event=att.event).exists()
        if not exists:
            event_date = att.event.event_date
            days_before = random.randint(1, 3)
            submit_time = timezone.make_aware(
                timezone.datetime.combine(event_date, timezone.datetime.min.time())
            ) - timedelta(days=days_before)
            reason = random.choice(REASONS)
            LeaveRequest.objects.create(
                enrollment=att.enrollment,
                event=att.event,
                reason=reason,
                submit_time=submit_time,
                approval_status=LEAVE_APPROVED,
                approver_notes=None,
            )
            count += 1
    print(f'已生成 {count} 条历史请假申请记录') 