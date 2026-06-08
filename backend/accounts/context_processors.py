from .models import Profile


def current_profile(request):
    profile = None
    sub = None
    pid = request.session.get("active_profile_id")
    if request.user.is_authenticated:
        if pid:
            profile = Profile.objects.filter(id=pid, user=request.user).first()
        sub = getattr(request.user, "subscription", None)
    return {"current_profile": profile, "current_subscription": sub}
