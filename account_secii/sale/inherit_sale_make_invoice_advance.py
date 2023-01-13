from odoo import models, api, _
from odoo.exceptions import ValidationError


class InheritSaleMakeAdvance(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for sale in sale_orders:
            if sale.is_prive:
                raise ValidationError(
                    _("Vous ne pouvez pas créer une facture pour une commande mis en instance !"))
        return super(InheritSaleMakeAdvance, self).create_invoices()
