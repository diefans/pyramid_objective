import inspect

import six

import objective
import objective.exc

from zope.interface import Interface, implementer, Attribute, classImplements, implementedBy
from zope.component import adapter

from pyramid.interfaces import IRequest, IResponse
from pyramid.httpexceptions import HTTPBadRequest


class IObjective(Interface):            # pylint: disable=E0239

    def __call__(validator=None, **kwargs):         # pylint: disable=E0213
        """Instantiation of Objective."""


class IObjectiveInvalidValue(Interface):        # pylint: disable=E0239
    node = Attribute("The node of the error.")
    value = Attribute("The value that caused the error.")
    message = Attribute("The message, that describes the error")


class IObjectiveInvalidChildren(IObjectiveInvalidValue):

    def error_dict():       # pylint: disable=E0211
        """:returns: a dict of all errors where key is a path tuple and value is the ``Invalid``"""


classImplements(objective.Mapping, IObjective)
classImplements(objective.exc.InvalidValue, IObjectiveInvalidValue)
classImplements(objective.exc.InvalidChildren, IObjectiveInvalidChildren)


class IObjectiveSubject(Interface):     # pylint: disable=E0239

    def get(name, default=None):        # pylint: disable=E0213
        """:returns: the named item or the default"""


class IObjectiveErrorResponse(IResponse):

    """Just a marker for error response."""


@implementer(IObjectiveSubject)
@adapter(IRequest)
class DefaultObjectiveSubject(dict):

    """Default adapter to build our objective subject."""

    def __init__(self, request):
        super(DefaultObjectiveSubject, self).__init__(
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


@implementer(IObjectiveErrorResponse)
@adapter(IObjectiveInvalidChildren)
class BadObjective(HTTPBadRequest):

    """We derive our exception context for specifically view on it."""

    def __init__(self, error):
        cnt = {
            'status': "error",
            'errors': [
                {
                    "location": path,
                    "name": path[-1],
                    "value": repr(invalid.value),
                    "message": invalid.message
                } for path, invalid in six.iteritems(error.error_dict())
            ]
        }

        super(BadObjective, self).__init__(json_body=cnt)


class Objection(object):

    """A request validator for objective."""

    def _get_objective(self, objective_class, *args, **kwargs):
        if IObjective in implementedBy(objective_class):
            _objective = objective_class(*args, **kwargs)

        else:
            _objective = objective_class

        return _objective

    def validate(self, request, objective_class, *args, **kwargs):

        """Perform request validation.

        There has to be an adapter registered to adapt ``IRequest`` into ``IObjectiveSubject``.

        :param request: the pyramid requst to validate
        :param objective_class: a IObjective implementer or provider
        :param args: arguments to instantiate an IObjective implementer
        :param kwargs: keyword arguments to instantiate an IObjective implementer
        """

        _objective = self._get_objective(objective_class, *args, **kwargs)
        subject = request.registry.getAdapter(request, IObjectiveSubject)

        try:
            validated = _objective.deserialize(
                subject,
                environment={
                    "request": request
                }
            )

            return validated

        except objective.exc.InvalidChildren as error:

            error_response = request.registry.getAdapter(error, IObjectiveErrorResponse)

            raise error_response


def includeme(config):
    """Register objection predicate."""

    # setup for pyramid
    config.registry.registerAdapter(BadObjective, provided=IObjectiveErrorResponse)
    config.registry.registerAdapter(DefaultObjectiveSubject)

    objection = Objection()

    def request_objective(request, objective_class, *args, **kwargs):

        return objection.validate(request, objective_class, *args, **kwargs)

    config.add_request_method(request_objective, "objective")
