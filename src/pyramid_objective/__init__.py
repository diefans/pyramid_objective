import objective

from pyramid.exceptions import PredicateMismatch
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config


class ObjectionMismatch(PredicateMismatch):

    """We derive our exception context for specifically view on it."""


@view_config(context=ObjectionMismatch, renderer="simplejson")
def objection_mismatch_view(ex, request):     # pylint: disable=W0613
    """We return a json error response as a 400/Bad Request."""

    cnt = {
        'status': "error",
        'errors': request.errors
    }

    return HTTPBadRequest(
        json_body=cnt,
    )


class Objection(object):

    """An validator for objective.

    An ``objective.Mapping`` is required,
    which has to have ``match``, ``params`` and ``body`` items.

    """

    # TODO think about using an IRequest adapter
    # for resolving what parts of the request object to

    def __init__(self, objective_class):
        self._objective = objective_class()

    def _find_body(self, request):
        # TODO maybe inspect content-type?
        try:
            body = request.json_body
            return body

        except ValueError:
            if request.POST:
                return request.POST

    def __call__(self, request):
        request_data = {
            'match': request.matchdict,
            'params': request.params
        }

        body = self._find_body(request)

        if body:
            request_data['body'] = body

        try:
            request.validated = self._objective.deserialize(
                request_data,
                environment={"request": request}
            )

            return True

        except objective.Invalid as e:
            # assemble request.errors
            for path, message in e.error_dict().iteritems():
                location = path[0]

                request.errors.add(location, '.'.join(path), message)

            raise ObjectionMismatch(e)

        return False


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
    config.add_view_predicate("objection", ObjectionPredicate)
