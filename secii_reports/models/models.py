# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMoveLineInherit(models.Model):

    _inherit = 'account.move.line'

    quantity = fields.Float(string='Quantity',
                            default=1.0, digits=(12,0),
                            help="The optional quantity expressed by this line, eg: number of product sold. "
                                 "The quantity is not a legal requirement but is very useful for some reports.")
    price_unit = fields.Float(string='Unit Price', digits=(12,0))


class SaleOrderLineInherit(models.Model):

    _inherit = 'sale.order.line'

    product_uom_qty = fields.Float(string='Quantity', digits=(12,0), required=True, default=1.0)
    price_unit = fields.Float('Unit Price', required=True, digits=(12,0), default=0.0)


class PurchaseOrderLineInherit(models.Model):

    _inherit = 'purchase.order.line'

    product_qty = fields.Float(string='Quantity', digits=(12,0), required=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits=(12,0))



