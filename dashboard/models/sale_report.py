from odoo import fields, models, api, tools


class SaleReportInherit(models.Model):
	_inherit = "sale.report"

	# montant_du = fields.Float(string="Montant du", readonly=True)
	# montant_total = fields.Float(string="Montant total", readonly=True)
	# ratio = fields.Float(string="Ratio", readonly=True)
	

	# def _query(self, with_clause='', fields={}, groupby='', from_clause=''):

		# fields['montant_du'] = ", SUM(l.montant_du) as montant_du"
		# fields['montant_total'] = ", SUM(l.montant_total) as montant_total"
		# fields['ratio'] = ", SUM(l.ratio_client) as ratio"
		

		# res = super(SaleReportInherit, self)._query(with_clause, fields, groupby, from_clause)
		# return res

	def _action_dashboard_sale(self):
		print("mon action _action_dashboard_sale exec", self)

		# Mise à jour des données de mouvement de facture
		# self._update_account_move_infos()
		action = {
			'name': "Tableau de bord BC + Devis",
			'type': "ir.actions.act_window",
			'res_model': 'sale.report',
			'view_mode': "dashboard",
			'search_view_id': self.env.ref('sale.view_order_product_search').id,
			'context': {
					'search_default_Sales': 1, 
					'search_default_Quotations': 1, 
					'search_default_filter_6_mth': 1, 
					'search_default_filter_date_last_month': 1
					},
			'view_id': self.env.ref('dashboard.sale_report_view_total_dashboard').id,
		}

		return action

	def _action_dashboard_sale_order(self):

		action = {
			'name': "Tableau de bord Bons de Commandes",
			'type': "ir.actions.act_window",
			'res_model': 'sale.report',
			'view_mode': "dashboard",
			'search_view_id': self.env.ref('sale.view_order_product_search').id,
			'context': {
					'search_default_Sales': 1, 
					'search_default_filter_6_mth': 1,
					'search_default_filter_date_last_month': 1
					},
			'view_id': self.env.ref('dashboard.sale_report_view_total_dashboard').id,
		}

		return action

	def _action_dashboard_sale_indicateurs(self):

		action = {
			'name': "Indicateurs Bons de Commandes",
			'type': "ir.actions.act_window",
			'res_model': 'sale.report',
			'view_mode': "dashboard",
			'search_view_id': self.env.ref('sale.view_order_product_search').id,
			'context': {
					'search_default_Sales': 1,
					'search_default_filter_6_mth': 1,
					'search_default_filter_date_last_month': 1
					},
			'view_id': self.env.ref('dashboard.sale_report_view_indicateurs_dashboard').id,
		}

		return action

	# Methode permettant de mettre a jour les données de mouvement de facture pour les clients
	def _update_account_move_infos(self):

		# Réccupération des factures clients
		account_ids = self.env['account.move'].search([('move_type', '=', 'out_invoice')])
		# Reccuperation des clients de ses factures
		partner_ids = account_ids.mapped('partner_id')
		print("Les partners", [partner.name for partner in partner_ids])

		montant_du = 0
		montant_total = 0
		ratio = 0
		for partner_id in partner_ids:
			for account_id in account_ids.filtered(lambda rec: rec.partner_id.id == partner_id.id):
				montant_du += account_id.amount_residual_signed
				montant_total += account_id.amount_total_signed

			ratio = 1 - montant_du/montant_total if montant_total != 0 else 0

			line_ids = self.env['sale.order.line'].search([('order_id.partner_id', '=', partner_id.id), ('state', '=', 'sale')])
			taille = line_ids.search_count([('order_id.partner_id', '=', partner_id.id), ('state', '=', 'sale')])
			# quotient_md = montant_du / taille if taille != 0 else 0
			# quotient_mt = montant_total / taille if taille != 0 else 0
			quotient_ratio = ratio/taille if taille != 0 else 0
			
			for line_id in line_ids:
				if quotient_ratio != 0:
					# print("Modification", partner_id.name)
					line_id.write({
						# 'montant_du': quotient_md,
						# 'montant_total': quotient_mt,
						'ratio_client': quotient_ratio
						})
			montant_du, montant_total = 0, 0

		for line_id in self.env['sale.order.line'].search([]):
			if not line_id.ratio_client:
				line_id.write({
						# 'montant_du': 0,
						# 'montant_total': 0,
						'ratio_client': 0
						})