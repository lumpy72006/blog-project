from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def should_hide_search(context):
    """
    Determines whether to hide the search bar based on the current view.
    Returns True if the search bar should be hidden.
    """
    request = context.get('request')
    if not request or not hasattr(request, 'resolver_match'):
        return False
    
    view_name = request.resolver_match.view_name
    app_name = request.resolver_match.app_name
    
    if app_name != 'blog':
        return False
    
    HIDE_SEARCH_VIEWS = {
        'blog:signup',
        'blog:login',
        'blog:create_post',
        'blog:edit_post',
        'blog:delete_post',
        'blog:post_detail',
    }
    
    return view_name in HIDE_SEARCH_VIEWS
