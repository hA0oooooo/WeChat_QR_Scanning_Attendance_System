from django.http import HttpResponse
import hashlib
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def wechat_notify(request):
    """
    用于微信服务器配置的消息验证接口
    """
    token = settings.WECHAT_TOKEN  # 使用settings中配置的token
    print("请求方法：", request.method)
    print("请求头：", request.headers)
    print("GET参数：", request.GET.dict())
    print("POST参数：", request.POST.dict())
    print("原始请求：", request)
    print("请求路径：", request.path)
    print("请求查询字符串：", request.META.get('QUERY_STRING', ''))
    
    if request.method == "GET":
        signature = request.GET.get('signature', '')
        timestamp = request.GET.get('timestamp', '')
        nonce = request.GET.get('nonce', '')
        echostr = request.GET.get('echostr', '')
        
        print("Token:", token)
        print("Signature:", signature)
        print("Timestamp:", timestamp)
        print("Nonce:", nonce)
        print("Echostr:", echostr)
        
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = ''.join(tmp_list)
        hash_str = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
        print("计算的hash:", hash_str)
        
        if hash_str == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse("验证失败")
    return HttpResponse("ok") 