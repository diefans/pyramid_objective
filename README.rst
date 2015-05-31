pyramid_objective
=================

You will simply get a request method `request.objective` to ensure your request objective.




.. code-block:: python

    from pyramid import view_config

    import objective


    def includeme(config):
        # include config somewhere
        config.include("pyramid_objective")
        config.add_route("foobar", "/foobar")


    class FooObjective(objective.BunchMapping)
        @objective.Item()
        class body(objective.Mapping):
            foo = objective.Item(objective.Unicode)
            bar = objective.Item(objective.Number)


    @view_config(route_name="foobar", request_method="POST")
    def view(request):

        validated = request.objective(FooObjective)

        assert isinstance(validated.body['foo'], unicode)
        assert isinstance(validated.body['bar'], (int, float))



The default objective subject is implemented like this:

.. code-block:: python

    class DefaultObjectiveSubject(dict):

        """Default adapter to build our objective subject."""

        implements(IObjectiveSubject)
        adapts(IRequest)

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
