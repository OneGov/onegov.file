import os

from AIS import AIS, PDF
from onegov.file.sign.generic import SigningService


class SwisscomAIS(SigningService, service_name='swisscom_ais'):
    """ A generic interface for various file signing services. """

    def __init__(self, customer, key_static, cert_file, cert_key):
        if not os.path.exists(cert_file):
            raise FileNotFoundError(cert_file)

        if not os.path.exists(cert_key):
            raise FileNotFoundError(cert_key)

        self.client = AIS(customer, key_static, cert_file, cert_key)

    def sign(self, infile, outfile):
        with self.materialise(infile) as fp:
            pdf = PDF(fp.name)
            self.client.sign_one_pdf(pdf)

        with open(pdf.out_filename, 'rb') as fp:
            for chunk in iter(lambda: fp.read(4096), b''):
                outfile.write(chunk)
