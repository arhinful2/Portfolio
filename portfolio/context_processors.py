from .models import Profile, SystemConfiguration


def build_navigation_items(visibility):
    items = [
        {
            'label': 'About',
            'href': '#about',
            'visible': bool(getattr(visibility, 'show_about', True)),
            'order': getattr(visibility, 'nav_about_order', 10),
        },
        {
            'label': 'Experience',
            'href': '#experience',
            'visible': bool(getattr(visibility, 'show_experience', False)),
            'order': getattr(visibility, 'nav_experience_order', 20),
        },
        {
            'label': 'Education',
            'href': '#education',
            'visible': bool(getattr(visibility, 'show_education', False)),
            'order': getattr(visibility, 'nav_education_order', 30),
        },
        {
            'label': 'Projects',
            'href': '#projects',
            'visible': bool(getattr(visibility, 'show_projects', False)),
            'order': getattr(visibility, 'nav_projects_order', 40),
        },
        {
            'label': 'Skills',
            'href': '#skills',
            'visible': bool(getattr(visibility, 'show_skills', False)),
            'order': getattr(visibility, 'nav_skills_order', 50),
        },
        {
            'label': 'Media',
            'href': 'media_gallery',
            'visible': bool(getattr(visibility, 'show_media', False)),
            'order': getattr(visibility, 'nav_media_order', 60),
            'is_url_name': True,
        },
        {
            'label': 'Contact',
            'href': '#contact',
            'visible': bool(getattr(visibility, 'show_contact', False)),
            'order': getattr(visibility, 'nav_contact_order', 70),
        },
    ]

    return sorted(
        [item for item in items if item['visible']],
        key=lambda item: item['order']
    )


def portfolio_context(request):
    """Add portfolio data to all templates"""
    try:
        profile = Profile.objects.first()
        system_config = SystemConfiguration.get_active()
        visibility = profile.visibility if profile else None  # type: ignore
        return {
            'portfolio_profile': profile,
            'portfolio_visibility': visibility,
            'navigation_items': build_navigation_items(visibility),
            'system_config': system_config,
        }
    except:
        return {
            'portfolio_profile': None,
            'portfolio_visibility': None,
            'navigation_items': [],
            'system_config': None,
        }
