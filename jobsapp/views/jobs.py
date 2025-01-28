from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from ..models import Favorite

@method_decorator(login_required, name='dispatch')
@method_decorator(require_POST, name='dispatch')
def toggle_favorite(request):
    """
    Toggle favorite status of a job
    """
    job_id = request.POST.get('job_id')
    if not job_id:
        return JsonResponse({'error': 'Job ID is required'}, status=400)

    try:
        favorite = Favorite.objects.filter(user=request.user, job_id=job_id)
        if favorite.exists():
            favorite.delete()
            return JsonResponse({
                'status': 'removed',
                'message': 'Job removed from favorites'
            })
        else:
            Favorite.objects.create(user=request.user, job_id=job_id)
            return JsonResponse({
                'status': 'added',
                'message': 'Job added to favorites'
            })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 