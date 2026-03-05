from .models import Profile, SystemConfiguration


def portfolio_context(request):
    """Add portfolio data to all templates"""
    try:
        profile = Profile.objects.first()
        system_config = SystemConfiguration.get_active()
        return {
            'portfolio_profile': profile,
            'portfolio_visibility': profile.visibility if profile else None,  # type: ignore
            'system_config': system_config,
        }
    except:
        return {
            'portfolio_profile': None,
            'portfolio_visibility': None,
            'system_config': None,
        }
