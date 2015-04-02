import objective

from zope.interface import Interface, implements
from zope.component import adapts

from pyramid.interfaces import IRequest
from pyramid.httpexceptions import HTTPBadRequest


class IObjectionSubject(Interface):     # pylint: disable=E0239

    def get(name, default=None):        # pylint: disable=E0213
        """:returns: the named item or the default"""


class DefaultObjectionSubject(dict):

    """Default adapter to build our objection subject."""

    implements(IObjectionSubject)
    adapts(IRequest)

    def __init__(self, request):
        super(DefaultObjectionSubject, self).__init__(
            match=request.matchdict,
            params=request.params
        )

        body = self._find_body(request)

        if body:
            self['body'] = body

    @staticmethod
    def _find_body(request):
        # TODO maybe inspect content-type?
        try:
            body = request.json_body
            return body

        except ValueError:
            if request.POST:
                return request.POST


class ObjectionMismatch(HTTPBadRequest):

    """We derive our exception context for specifically view on it."""


class Objection(object):

    """An validator for objective.

    An ``objective.Mapping`` is required,
    which has to have ``match``, ``params`` and ``body`` items.

    """

    def __init__(self, objective_class):
        self._objective = objective_class()

    def __call__(self, request):
        subject = request.registry.getAdapter(request, IObjectionSubject)

        try:
            request.validated = self._objective.deserialize(
                subject,
                environment={"request": request}
            )

            return True

        except objective.Invalid as e:
            # assemble request.errors
            for path, message in e.error_dict().iteritems():
                location = path[0]

                request.errors.add(location, '.'.join(path), message)

            cnt = {
                'status': "error",
                'errors': request.errors
            }

            raise ObjectionMismatch(json_body=cnt)


class ObjectionPredicate(object):

    """Just deserialize the request by the provided objective.
    Adds errors to request.errors.
    """

    def __init__(self, objective_class, config):    # pylint: disable=W0613
        self.objective_class = objective_class
        self.objection = Objection(objective_class)

    def text(self):
        return 'objective = {}'.format(self.objective_class)

    phash = text

    def __call__(self, context, request):

        return self.objection(request)


def includeme(config):
    """Register objection predicate."""

    # setup for pyramid
    config.registry.registerAdapter(DefaultObjectionSubject)
    config.add_view_predicate("objection", ObjectionPredicate)
