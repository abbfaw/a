from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
# from twilio.rest import Client

from odoo.http import request

from io import BytesIO

try:
    import qrcode
except ImportError:
    qrcode = None
try:
    import base64
except ImportError:
    base64 = None


class SaleOrder(models.Model):
    _inherit = "sale.order"

    old_partner = fields.Many2one('res.partner')
    new_partner = fields.Many2one('res.partner')
    qr_code = fields.Binary('QRcode', compute="_generate_qr")

    def _generate_qr(self):
        """Méthode pour générer un code QR"""
        for rec in self:
            if qrcode and base64:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=3,
                    border=4,
                )
                qr.add_data("Test")
                # qr.add_data(rec.url)
                qr.make(fit=True)
                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())
                rec.update({'qr_code': qr_image})
            else:
                raise UserError(_('Les exigences nécessaires pour exécuter cette opération ne sont pas satisfaites.'))

    # def send_sms_twilio(self):
    #     account_sid = 'AC0eacc095b5eec03c72edcc0f5fe748ec'
    #     auth_token = '2c019396c313b3e1179028804a056454'
    #     client = Client(account_sid, auth_token)
    #     number = ''.join(self.partner_id.phone.split(' '))
    #     print("Number", number)
    #     body = "Votre commande a été validé, vous serez livré(e) dans 24h. Merci de nous faire confiance! "
    #     from_ = '+15108226061'
    #     # to = "+2250757110861"
    #     try:
    #         message = client.messages.create(body=body, from_=from_, to=number)
    #         print(message.body, f"{self.partner_id.name}")
    #     except:
    #         print("Vérifiez votre numéro de telephone")

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        params = self.env['ir.config_parameter'].sudo().search([('key', '=', 'mediano_website.sms_on_confirm')])
        if params:
            checked = params.value
            if checked:
                # self.send_sms_twilio()
                pass
            else:
                pass
        else:
            pass
        print("*****************************************Ok************************************")
        return res
