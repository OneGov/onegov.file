import os

from AIS import AIS as AISBase
from AIS import PDF
from onegov.file.sign.generic import SigningService
from uuid import uuid4


class AIS(AISBase):
    """ Customises AIS to always remember the last issued request-id. """

    def _request_id(self):
        self.last_request_id = uuid4().hex
        return self.last_request_id


class SwisscomAIS(SigningService, service_name='swisscom_ais'):
    """ Sign PDFs using Swisscom's All-In Signing Service. """

    def __init__(self, customer, key_static, cert_file, cert_key):
        if not os.path.exists(cert_file):
            raise FileNotFoundError(cert_file)

        if not os.path.exists(cert_key):
            raise FileNotFoundError(cert_key)

        self.customer = customer
        self.client = AIS(customer, key_static, cert_file, cert_key)

    def sign(self, infile, outfile):
        with self.materialise(infile) as fp:
            pdf = PDF(fp.name)
            self.client.sign_one_pdf(pdf)

        with open(pdf.out_filename, 'rb') as fp:
            for chunk in iter(lambda: fp.read(4096), b''):
                outfile.write(chunk)

        return f'swisscom_ais/{self.customer}/{self.client.last_request_id}'
