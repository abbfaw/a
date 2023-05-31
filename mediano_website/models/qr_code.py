from io import BytesIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError

try:
    import qrcode
except ImportError:
    qrcode = None
try:
    import base64
except ImportError:
    base64 = None


class S(models.Model):
    _name = ''
    qr_code = fields.Binary('QRcode', compute="_generate_qr")

    def _generate_qr(self):
        """method to generate QR code"""
        for rec in self:
            if qrcode and base64:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=3,
                    border=4,
                )
                qr.add_data("Product : ")
                qr.add_data(rec.name)
                qr.add_data(", Reference : ")
                qr.add_data(rec.default_code)
                qr.add_data(", Price : ")
                qr.add_data(rec.list_price)
                qr.add_data(", Quantity : ")
                qr.add_data(rec.qty_available)
                qr.make(fit=True)
                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())
                rec.update({'qr_code': qr_image})
            else:
                raise UserError(_('Les exigences nécessaires pour exécuter cette opération ne sont pas satisfaites.'))
