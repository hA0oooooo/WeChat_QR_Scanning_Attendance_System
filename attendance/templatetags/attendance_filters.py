from django import template
from django.utils import timezone
import pytz

register = template.Library()

@register.filter
def to_local_time(value):
    """将UTC时间转换为本地时间（UTC+8）"""
    if value is None:
        return value
    if not timezone.is_aware(value):
        value = timezone.make_aware(value)
    return timezone.localtime(value, timezone=pytz.timezone('Asia/Shanghai'))

@register.filter
def to(value, end):
    """生成从value到end的数字范围"""
    try:
        start = int(value)
        end = int(end)
        return range(start, end + 1)
    except (ValueError, TypeError):
        return [] 