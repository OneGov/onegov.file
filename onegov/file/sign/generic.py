import os.path

from contextlib import contextmanager
from tempfile import TemporaryFile


class SigningService(object):
    """ A generic interface for various file signing services. """

    registry = {}

    def __init_subclass__(cls, service_name, **kwargs):
        SigningService.registry[service_name] = cls
        cls.service_name = service_name

        super().__init_subclass__(**kwargs)

    @staticmethod
    def for_config(config):
        """ Spawns a service instance using the given config. """

        return SigningService.registry[config['name']](
            **config.get('parameters', {})
        )

    def __init__(self, **parameters):
        """ Signing services are initialised with parameters of their chosing.

        Typically those parameters are read from a yaml file::

            name: service_name
            paramters:
                foo: bar
                bar: foo

        """

        self.parameters = parameters

    def sign(self, infile, outfile):
        """ Signs the input file and writes it to the given output file.

        If the input-file exists on disk, its ``file.name`` attribute points
        to an existing path.

        Sublcasses may add extra parameters to this signing function, though
        it is expected that they all have a default value set.

        So it is okay to do this::

            def sign(self, infile, outfile, foo)

        But it would be better to do thiss::

            def sign(self, infile, outfile, foo='bar')

        """

        raise NotImplementedError

    @contextmanager
    def materialise(self, file):
        """ Takes the given file-like object and ensures that it exists
        somewhere on the disk during the lifetime of the context.

        """
        file.seek(0)

        if os.path.exists(file.name):
            yield file
        else:
            with TemporaryFile('rb+') as output:
                for chunk in iter(lambda: file.read(4096), b''):
                    output.write(chunk)

                output.seek(0)

                yield output
