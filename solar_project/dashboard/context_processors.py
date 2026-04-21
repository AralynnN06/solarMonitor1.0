from .models import UserProfile


def seeded_status(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {"is_seeded": None}

    profile = UserProfile.objects.filter(user=request.user).only("has_seeded_data").first()
    return {"is_seeded": profile.has_seeded_data if profile else False}
