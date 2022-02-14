from django.utils import timezone


def year(request):
    """Добавляет в контекст переменную greeting с приветствием."""
    current_datetime = timezone.now()
    return {
        'year': current_datetime.year,
    }
