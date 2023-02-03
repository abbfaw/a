from odoo import fields, api, models

class PurchaseReportInherit(models.Model):
	_inherit = "purchase.report"

	@api.model
	def read_group(self, domain, fields, groupby, offset=0, limit=20, orderby=False, lazy=False):
    	# print("Le read_group de pos", self)
		res = super(PurchaseReportInherit, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
		return res