
from odoo import api, fields, models,_


class InheritStockPicking(models.Model):
    _inherit = 'stock.picking'

    is_prive = fields.Boolean(string='EN INSTANCE')

    @api.model
    def create(self, vals_list):
        private_sale = self.env['sale.order'].search([('name', '=', vals_list.get('origin'))]).is_prive
        private_purchase = self.env['purchase.order'].search([('name', '=', vals_list.get('origin'))]).is_prive
        if private_sale:
            vals_list.update({'is_prive': private_sale})
        elif private_purchase:
            vals_list.update({'is_prive': private_purchase})
        return super(InheritStockPicking, self).create(vals_list)

    @api.onchange('is_prive')
    def onchange_is_private(self):
        search_name_sale = self.env['sale.order'].search([('name', '=', self.origin)])
        search_name_purchase = self.env['purchase.order'].search([('name', '=', self.origin)])
        origin = self.env['account.move'].search([('invoice_origin', '=', self.origin)])
        if origin:
            warning_mess = {
                'title': _('Avertissement!'),
                'message': _("Vous ne pouvez pas mettre en instance une livraison dont la commande est associée à une "
                             "facture !")
            }
            return {'warning': warning_mess, 'value': {'is_prive': False}}
        else:
            if search_name_sale:
                search_name_sale.write({'is_prive': self.is_prive})
            elif search_name_purchase:
                search_name_purchase.write({'is_prive': self.is_prive})



