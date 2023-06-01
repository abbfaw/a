from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
# from twilio.rest import Client

from odoo.http import request

from io import BytesIO


class SaleOrder(models.Model):
    _inherit = "sale.order"

    old_partner = fields.Many2one('res.partner')
    new_partner = fields.Many2one('res.partner')
