from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import fields, http
from odoo.http import request
from twilio.rest import Client

import logging

_logger = logging.getLogger(__name__)


def send_sms_twilio(number):
    account_sid = 'AC97b378286da1084e29a2c3e05cd91163'
    auth_token = '10de6977bc7d336d0e80738c8686bf9e'
    client = Client(account_sid, auth_token)
    try:
        message = client.messages.create(
            body="Votre commande a été validé, vous serez livré(e) dans 24h. Merci de nous faire confiance! Progistack",
            from_='+19035609396',
            to=number
        )
        print("Message body", message.body)
    except Exception as e:
        print("Vérifiez votre numéro de telephone")
        raise e


class WebsiteSaleInherit(WebsiteSale):
    phone_number = ''

    # @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    # def address(self, **kw):
    #     res = super(WebsiteSaleInherit, self)
    #     if kw:
    #         self.phone_number = kw.get('phone')
    #         print("res kw",kw)
    #         # if phone_number:
    #         #     return phone_number
    #     return res.address(kw)

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    def shop_payment_confirmation(self, **post):
        res = super(WebsiteSaleInherit, self).shop_payment_confirmation()
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            print("1er if de paiement", self.phone_number)
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            if order:
                print("2eme if de order", order)
                send_sms_twilio('+2250564261890')

        return res
