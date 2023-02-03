from odoo import fields, models, api


class AccountMove(models.Model):
	_inherit = "account.move"

	# partner_id = fields.Many2one('res.partner', readonly=True, tracking=True,
    #     states={'draft': [('readonly', False)]},
    #     check_company=True,
    #     string='Partner', change_default=True, inverse_name='account_move_ids')
	# sale_report_id = fields.Many2one('account.move', string='Rapport de vente')

	def write(self, vals):

		print("Le write de AccountMove", self, vals)

		for move in self:
			print("Dans le self", move.amount_residual, sum([ml.price_subtotal for ml in move.invoice_line_ids]))
			move.partner_id.montant_du = move.amount_residual
			move.partner_id.montant_total = sum([ml.price_subtotal for ml in move.invoice_line_ids])
			move.partner_id.ratio_client = 1 - move.amount_residual_signed / move.amount_total_signed if move.amount_total_signed != 0 else 0

		res = super(AccountMove, self).write(vals)

		return res