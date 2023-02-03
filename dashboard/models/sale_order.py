from odoo import fields, api, models

class SaleOrderLineInherit(models.Model):
	_inherit = "sale.order.line"

	# montant_du = fields.Float(string="Montant dû")
	# montant_total = fields.Float(string="Montant total")
	ratio_client = fields.Float(string="Ratio client")