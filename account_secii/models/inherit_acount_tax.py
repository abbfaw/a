from odoo import fields, models, api


class InheritAccountTax(models.Model):
    _inherit = 'account.tax'

    exclude_tax = fields.Boolean(string='TVA non facturée')
    exclude_amount = fields.Float(string='coéfficient')