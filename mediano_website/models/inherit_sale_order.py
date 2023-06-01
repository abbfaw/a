# from odoo.tools import  float_round

from odoo import api, models, fields, _
from odoo.http import request


class SaleOrderDelivery(models.Model):
    _inherit = 'sale.order'

    stick = fields.Boolean()
    state = fields.Selection(selection_add=[('livre', "Livré"), ('encours', "En cours de Livraison")])

    @api.model
    def is_public_user(self):
        print('ZZZZ', request.website._get_cached('user_id'))
        return request.env.user.id == request.website._get_cached('user_id')

    def livrer(self):
        print('Livré')
        for rec in self:
            rec.state = 'livre'

    def encours(self):
        print('En cours de Livraison')
        for rec in self:
            rec.state = 'encours'


class PaymentProviderInherit(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('cash', "Paiement en Espèces")], ondelete={'cash': 'set default'})
