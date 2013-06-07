from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth import authenticate
from django.conf import settings
from django.db import transaction
from django.contrib.auth import logout as _logout
from django.contrib.auth import login as _login
from collections import OrderedDict
import floppyforms as forms
from models import Member, Session



def context_processor(request):
    """Run to provide every template context with some standard variables"""
    ctx = {'TITLE': 'Iffley Fields Woodcraft Folk Elfins Group'}
    ctx['static_url'] = settings.STATIC_URL
    if request.user.is_authenticated():
        ctx['username'] = request.user.username
    return ctx


def dodoc(text):
    if text is None:
        return None, None
    lines = [line.strip() for line in text.split('\n')]
    title = lines[0]
    paragraphs = ['']
    for line in lines[1:]:
        if line != '':
            paragraphs[-1] = line if paragraphs[-1] == '' else paragraphs[-1] + ' ' + line
        else:
            paragraphs = paragraphs + [''] if paragraphs[-1] != '' else paragraphs
    return title, paragraphs


class AuthenticationError(StandardError):
    app = "wfm"


def login_form(request, ctx):
    ctx['authenticationform'] = forms.AuthenticationForm()
    t = loader.get_template('login.html')
    return HttpResponse(t.render(RequestContext(request, ctx)))


def requireSession(view):
    def session_wrapper(request, db=None, ctx=None):
        ctx = {} if ctx is None else ctx
        try:
            doc = view.__doc__ if hasattr(view, '__doc__') else None
            ctx['help_title'], ctx['help_text'] = dodoc(doc)
            if request.user.is_authenticated():
                return view(request, db, ctx)
            elif 'username' in request.POST and 'password' in request.POST: #?move
                user = authenticate(username=request.POST['username'], password=request.POST['password'])
                if user is not None:
                    if user.is_active:
                        with transaction.commit_on_success():
                            _login(request, user)
                            ctx['app_messages'] = ['Login successful']
                            return _home(request, db, ctx)
                    else:
                        raise AuthenticationError('Login failed: inactive user.')
                else:
                    raise AuthenticationError('Login failed: non-existent username or incorrect password')
            else:
                raise AuthenticationError('Not currently authenticated')
        except AuthenticationError, e:
            ctx['app_messages'] = [e.message or str(e)]
            return login_form(request, ctx)
        except StandardError, e:
            ctx['app_messages'] = [e.message or str(e)]
            return _home(request, db, ctx)
        except Exception, e:
            raise e

    return session_wrapper


def counts(members):
    return [len(Member.boys(members)), len(Member.girls(members)), len(members)]


def _home(request, db=None, ctx=None):
    t = loader.get_template('home.html')
    ctx['summary'] = OrderedDict([
        ('Waiting', counts(Member.waiters())),
        ('Elfin', counts(Member.elfins())),
        ('Woodchip', counts(Member.woodchips())),
        ('Carer', counts(Member.carers())),
    ])
    ctx['Member'] = Member

    return HttpResponse(t.render(RequestContext(request, ctx)))


def home(request, db=None, ctx={}):
    """ Home
    Summary
    """
    return _home(request, db, ctx)


@requireSession
def logout(request, db=None, ctx={}):
    """You have been logged out.

    Login to proceed.
    """
    session_id = request.session.session_key
    _logout(request)
    request.session.logged_out = True
    ctx['app_messages'] = ['You have been logged out']

    return _home(request, db, ctx)

@requireSession
def login(request, db=None, ctx={}):
    """Login

    Enter Authentication details.
    """
    return _home(request, db, ctx)


def _carers(request, db=None, ctx={}):
    t = loader.get_template('carers.html')
    ctx['carers'] = Member.carers()
    return HttpResponse(t.render(RequestContext(request, ctx)))

@requireSession
def carers(request, db=None, ctx={}):
    """Carers

    Carers with expiry dates.
    """
    return _carers(request, db, ctx)


def _members(request, db=None, ctx={}):
    t = loader.get_template('members.html')
    try:
        status = request.REQUEST['status']
    except StandardError:
        status = 'Elfin'
    ctx['status'] = status
    ctx['members'] = Member.members_with_status(status)
    return HttpResponse(t.render(RequestContext(request, ctx)))

@requireSession
def members(request, db=None, ctx={}):
    """Members

    """
    return _members(request, db, ctx)


def _member(request, db=None, ctx={}):
    username = request.REQUEST['username']
    if username is None:
        raise AppError("Parameter 'username' missing from request")
    t = loader.get_template('member.html')
    try:
        ctx['member'] = Member.objects.get(username=request.REQUEST['username'])
    except Member.DoesNotExist:
        raise AppError("Nonexistent username '%s' given" % username)
    return HttpResponse(t.render(RequestContext(request, ctx)))

@requireSession
def member(request, db=None, ctx={}):
    """Member

    A members details.
    """
    return _member(request, db, ctx)


def _session(request, db=None, ctx={}):
    try:
        name = request.REQUEST['name']
    except StandardError:
        name = None
        t = loader.get_template('session.html')
        ctx['SessionChoiceForm'] = forms.SessionChoiceForm()
        ctx['sessions'] = Session.objects.all()

        return HttpResponse(t.render(RequestContext(request, ctx)))
    t = loader.get_template('members.html')
    ctx['members'] = Member.attendees(name)
    return HttpResponse(t.render(RequestContext(request, ctx)))

@requireSession
def session(request, db=None, ctx={}):
    """Session

    A Session.
    """
    return _session(request, db, ctx)
