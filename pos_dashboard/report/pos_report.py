from odoo import fields, api, models


class PosOrderReportInherit(models.Model):
    _inherit = "report.pos.order"

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=20, orderby=False, lazy=False):
    	print("Le read_group de pos", self)
    	res = super(PosOrderReportInherit, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
    	return res
    # @api.model
	# def read_group(self):

	# 	res = super(PosOrderReportInherit, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
	# 	return res