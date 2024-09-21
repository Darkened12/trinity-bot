class Async:
    """Every attribute that will be constructed with _init() must pre-exist on __init__ with None as its value """

    def __await__(self):
        return self._init().__await__()

    def __getattribute__(self, item):
        attr = super().__getattribute__(item)
        if attr is None:
            raise AttributeError(f'Object instantiation must be awaited before usage: await Async()')
        return attr

    @staticmethod
    def constructor(coroutine):
        async def wrapper(*args, **kwargs):
            await coroutine(*args, **kwargs)
            return args[0]
        return wrapper

    async def _init(self):
        """This should be overridden"""
        pass
