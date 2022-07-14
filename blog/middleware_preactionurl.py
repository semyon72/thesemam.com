# Project: blog_7myon_com
# Package: 
# Filename: middleware_preactionurl.py
# Generated: 2021 Jul 11 at 19:41 
# Description of <middleware_preactionurl>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.http import HttpRequest

PREACTION_URL_SESSION_KEY='middleware_preaction_url'
PREACTION_REQUEST_ATTR_NAME='preaction_url'


def preaction_url(request: HttpRequest, session_key):
    result = ''
    # JSON serializer does not support deque objects
    # therefore either need convert to tuple or list and same to back
    # or use list with with implementation of deque and maxlen=2 logic
    urls = request.session.get(session_key, [])[-2:]
    # request.get_full_path()  returns like /fff/fff?prm=prm and safe (escaped ...) for further using
    url = request.get_full_path()
    # # request.path returns like /fff/fff and not safe for using
    # path = request.path
    if request.method == 'GET':
        turls = []
        for u in urls:
            if url != u:
                turls.append(u)
            else:
                break
        turls.append(url)
        urls = turls[-2:]

    else:  # suppose POST, PUT, DELETE ... methods
        # url_obj = urlsplit(url)._replace(scheme='', netloc='')
        # if is_valid_path(url_obj.path):
        if urls:
            last = urls.pop()
            assert len(urls) < 2, 'Now urls must contain 0 or 1 element'
            if last == url and urls:
                result = urls[0]
            urls = []

    if urls:
        request.session[session_key] = urls
    else:
        request.session.pop(session_key, None)

    return result


# it could be inherited from django.utils.deprecation.MiddlewareMixin
class PreActionUrlMiddleware:
    """
    It tracks for GET requests and collect the last two.
    If request differ to GET (POST for example) then it compare  with last GET and
    if they equal then will returned the first.
    This works enough good if do some actions sequently on one tab of browser but
    if something doing in parallel but during one session it might return url
    a reference on last page requested on other tab.
    Example of using:
        preaction_url = getattr(self.request, 'preaction_url', '')
        if preaction_url:
            return preaction_url
    """

    def __init__(self, get_request) -> None:
        # it happens at load middleware stage
        self.get_request = get_request

    def __call__(self, request):
        # it happens at execution of middleware stage
        # right before the next middleware will be executed
        result = self.get_request(request)
        # now we have response that is response
        return result

    def process_view(self, request, view_func, view_args, view_kwargs):
        # it happens right before view will be executed
        # check request path from settings and users.is_staff ....
        url = preaction_url(request, PREACTION_URL_SESSION_KEY)
        if url:
            setattr(request, PREACTION_REQUEST_ATTR_NAME, url)
        # if returns None then main flow will not interrupted
