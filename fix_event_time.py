from attendance.models import AttendanceEvent
from django.utils import timezone
from datetime import datetime

event = AttendanceEvent.objects.filter(event_date='2025-06-25').first()
if event:
    event.event_date = datetime(2025, 6, 16).date()
    event.scan_start_time = timezone.make_aware(datetime(2025, 6, 16, 13, 30, 0))
    event.scan_end_time = timezone.make_aware(datetime(2025, 6, 16, 17, 5, 0))
    event.save()
    print('考勤事件已改为6月16日13:30-17:05')
else:
    print('未找到原6月25日考勤事件') 