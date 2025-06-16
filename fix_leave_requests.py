import os
import django
import random
from datetime import datetime, timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from attendance.models import AttendanceEvent, Attendance, LeaveRequest, Teacher
from django.utils import timezone

# 原因与意见对应表
reason_opinion_map = {
    "病假": ["注意身体", "祝早日康复", "同意", "批准"],
    "事假": ["同意", "已阅", "批准", "下次提前请假"],
    "婚丧": ["同意", "批准", "节哀顺变"],
    "家庭原因": ["同意", "已阅"],
    "外出比赛": ["同意", "批准", "加油"],
    "临时有事": ["同意", "已阅", "批准"],
    "身体不适": ["注意身体", "祝早日康复", "同意"]
}

leave_reasons = list(reason_opinion_map.keys())
teacher = Teacher.objects.first()
base_date = timezone.now().date()
events = AttendanceEvent.objects.filter(event_date__lt=base_date)
event_ids = [e.event_id for e in events]
count = 0

for lr in LeaveRequest.objects.filter(event_id__in=event_ids):
    reason = random.choice(leave_reasons)
    approver_notes = random.choice(reason_opinion_map[reason])
    # 生成合理的申请时间
    leave_date = lr.event.event_date
    start_date = datetime(2025, 5, 1)
    end_date = datetime.combine(leave_date, datetime.min.time()) - timedelta(days=1)
    if end_date < start_date:
        submit_time = start_date
    else:
        delta = (end_date - start_date).days
        random_days = random.randint(0, max(delta, 0))
        random_hour = random.randint(8, 18)
        random_minute = random.randint(0, 59)
        submit_time = start_date + timedelta(days=random_days, hours=random_hour, minutes=random_minute)
    lr.reason = reason
    lr.approver_notes = approver_notes
    lr.approver = teacher
    lr.approval_status = 2
    lr.submit_time = timezone.make_aware(submit_time)
    if not lr.approval_timestamp:
        lr.approval_timestamp = timezone.now()
    lr.save()
    count += 1

print(f'已强制覆盖所有请假条 {count} 条，并随机生成合理申请时间。') 