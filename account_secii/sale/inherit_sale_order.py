from odoo import api, fields, models, _


class InheritSaleOrder(models.Model):
    _inherit = 'sale.order'

    is_prive = fields.Boolean(default=True)
    user_con = fields.Boolean(compute='get_user_connect')

    def get_user_connect(self):
        for user in self:
            res_user = self.env['res.users'].search([('id', '=', self._uid)])
            if res_user.has_group('account_secii.sale_secii_box_see_all') and not res_user.has_group('account_secii'
                                                                                                  '.sale_secii_users'):
                user.user_con = True
            else:
                user.user_con = False
        return True

    @api.onchange('is_prive')
    def onchange_is_private(self):
        print('nameeeeeeeeeeeeeee', self.name)
        search_name = self.env['stock.picking'].search([('origin', '=', self.name)])
        origin = self.env['account.move'].search([('invoice_origin', '=', self.name)])
        if origin:
            warning_mess = {
                'title': _('Avertissement!'),
                'message': _("Vous ne pouvez pas mettre en instance une vente dont vous avez crée une facture !")
            }
            return {'warning': warning_mess, 'value': {'is_prive': False}}
        else:
            if search_name:
                search_name.write({'is_prive': self.is_prive})
