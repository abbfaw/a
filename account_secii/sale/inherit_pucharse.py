from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class InheritSaleOrder(models.Model):
    _inherit = 'purchase.order'

    is_prive = fields.Boolean(default=True)

    @api.onchange('is_prive')
    def onchange_is_private(self):
        search_name = self.env['stock.picking'].search([('origin', '=', self.name)])
        origin = self.env['account.move'].search([('invoice_origin', '=', self.name)])
        if origin:
            warning_mess = {
                'title': _('Avertissement!'),
                'message': _("Vous ne pouvez pas mettre en instance une commande dont vous avez crée une facture !")
            }
            return {'warning': warning_mess, 'value': {'is_prive': False}}
        else:
            if search_name:
                search_name.write({'is_prive': self.is_prive})

    def action_create_invoice(self):
        for line in self:
            if line.is_prive:
                raise ValidationError(
                    _("Vous ne pouvez pas créer une facture pour une commande mis en instance !"))
        return super(InheritSaleOrder, self).action_create_invoice()
