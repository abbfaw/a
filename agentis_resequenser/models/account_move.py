from odoo import fields, models


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    def action_open_resequence_view(self):
        return self.env['ir.actions.act_window']._for_xml_id('account.action_account_resequence')
