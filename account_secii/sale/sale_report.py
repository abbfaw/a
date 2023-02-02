from odoo import fields, api, models

class SaleReportInherit(models.Model):
	_inherit = "sale.report"

	commune = fields.Selection([('abobo', "Abobo"),
								('adjamé', "Adjamé"),
								('anyama', "Anyama"),
								('attécoubé', "Attécoubé"),
								('bingerville', "Bingerville"),
								('cocody', "Cocody"),
								('koumassi', "Koumassi"),
								('marcory', "Marcory"),
								('plateau', "Plateau"),
								('portbouët', "Port Bouët"),
								('treichville', "Treichville"),
								('songon ', "Songon"),
								('yopougon', "Yopougon"),
								],
							   string="Communes", readonly=True)

	def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
		print("Le new _query")
		fields['commune'] = ", partner.commune as commune"
		groupby += ', partner.commune'

		return super(SaleReportInherit, self)._query(with_clause, fields, groupby, from_clause)

	def _update_account_move_infos(self):
		print("Le new update")
		synthese_ids = self.env['secii.synthese'].search([])
		for synthese_id in synthese_ids:
			line_ids = self.env['sale.order.line'].search([('order_id.partner_id', '=', synthese_id.client.id)])
			for line_id in line_ids:
				line_id.write({
						'ratio_client': (synthese_id.somme_payee / synthese_id.total_commandes) / line_ids.search_count([('order_id.partner_id', '=', synthese_id.client.id)]) if synthese_id.total_commandes != 0 else 0
					})