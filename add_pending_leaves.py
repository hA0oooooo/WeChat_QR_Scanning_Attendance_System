import os
import django
import random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from attendance.models import AttendanceEvent, LeaveRequest, Enrollment, Student
from django.utils import timezone

event = AttendanceEvent.objects.get(event_date='2025-06-16')
students = list(Student.objects.exclude(stu_id='23307130001'))
selected = random.sample(students, k=random.randint(2, 3))
for stu in selected:
    enrollment = Enrollment.objects.get(student=stu, course=event.course)
    lr, created = LeaveRequest.objects.get_or_create(
        enrollment=enrollment,
        event=event,
        defaults={'reason': '事假', 'approval_status': 1, 'submit_time': timezone.now()}
    )
    lr.reason = '事假'
    lr.approval_status = 1
    lr.submit_time = timezone.now()
    lr.save()
    print(f'{stu.stu_name}已设为待审批请假') 