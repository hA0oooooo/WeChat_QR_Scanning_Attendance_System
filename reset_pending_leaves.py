import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from attendance.models import LeaveRequest, Attendance, STATUS_ABSENT

pending_leaves = LeaveRequest.objects.filter(approval_status=1)
for lr in pending_leaves:
    att = Attendance.objects.filter(enrollment=lr.enrollment, event=lr.event).first()
    if att and att.status != STATUS_ABSENT:
        att.status = STATUS_ABSENT
        att.save()
        print(f"{lr.enrollment.student.stu_name}的考勤已改为缺勤")
print("所有待审批请假条对应考勤已改为缺勤。") 