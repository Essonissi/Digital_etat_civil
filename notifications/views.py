from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
import logging

from .models import Notification
from comptes.decorators import role_required

logger = logging.getLogger(__name__)

@login_required
@role_required('citoyen')
@require_GET
def notifications_citoyen(request):
    """Récupère les notifications pour l'interface"""
    # Paramètres
    limit = int(request.GET.get('limit', 10))
    page = int(request.GET.get('page', 1))
    only_unread = request.GET.get('unread', 'true') == 'true'
    
    # Query
    queryset = Notification.objects.filter(user=request.user, archive=False)
    if only_unread:
        queryset = queryset.filter(lu=False)
    
    # Pagination
    paginator = Paginator(queryset, limit)
    notifications = paginator.get_page(page)
    
    data = []
    for notif in notifications:
        data.append({
            'id': notif.id,
            'title': notif.titre,
            'message': notif.message,
            'type': notif.type,
            'priority': notif.priority,
            'read': notif.lu,
            'time': notif.date_creation.strftime("%d/%m/%Y %H:%M"),
            'action_url': notif.action_url,
            'action_label': notif.action_label,
            'is_urgent': notif.is_urgent,
        })

    return JsonResponse({
        'notifications': data,
        'count': queryset.count(),
        'unread_count': Notification.objects.filter(user=request.user, lu=False).count(),
        'has_next': notifications.has_next(),
        'has_previous': notifications.has_previous(),
    })


@login_required
@require_POST
@ensure_csrf_cookie
def marquer_lue(request, notif_id):
    """Marque une notification comme lue"""
    try:
        notif = get_object_or_404(
            Notification, 
            id=notif_id, 
            user=request.user,
            archive=False
        )
        
        notif.lu = True
        notif.date_lecture = timezone.now()
        notif.save(update_fields=['lu', 'date_lecture'])
        
        logger.info(f"Notification {notif_id} marquée comme lue par {request.user}")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Notification marquée comme lue',
            'unread_count': Notification.objects.filter(user=request.user, lu=False).count()
        })
        
    except Exception as e:
        logger.error(f"Erreur marquage notification {notif_id}: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Erreur lors du marquage'
        }, status=500)


@login_required
@require_POST
@ensure_csrf_cookie
def marquer_toutes_lues(request):
    """Marque toutes les notifications comme lues"""
    try:
        count = Notification.objects.mark_as_read(request.user)
        logger.info(f"{count} notifications marquées comme lues pour {request.user}")
        
        return JsonResponse({
            'status': 'success',
            'message': f'{count} notifications marquées comme lues',
            'count': count
        })
        
    except Exception as e:
        logger.error(f"Erreur marquage en masse: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Erreur lors du marquage'
        }, status=500)


@login_required
@require_POST 
@ensure_csrf_cookie
def archiver_notification(request, notif_id):
    """Archive une notification"""
    try:
        notif = get_object_or_404(Notification, id=notif_id, user=request.user)
        notif.archive = True
        notif.lu = True
        notif.save(update_fields=['archive', 'lu'])
        
        return JsonResponse({
            'status': 'success',
            'message': 'Notification archivée'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': 'Erreur lors de l\'archivage'
        }, status=500)