from django.http import JsonResponse


def test_csrf(request):
    response = JsonResponse({'csrf_token': request.COOKIES.get('csrftoken')})
    print(f"CSRF Token: {request.COOKIES.get('csrftoken')}")
    return response
