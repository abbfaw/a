from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class InheritSaleOrder(models.Model):
    _inherit = 'sale.order'

    is_prive = fields.Boolean(default=True)
    user_con = fields.Boolean(compute='get_user_connect')
    # limit = fields.Boolean(default=True)
    credit_limite = fields.Monetary()

    @api.onchange('partner_id')
    def recherche_credit_dispo(self):
        print('Channnngé')
        if self.partner_id.plafond > 0:
            if self.partner_id.test <= 0:
                # self.limit = False
                self.credit_limite = self.partner_id.plafond
        elif self.partner_id.plafond == self.partner_id.test == 0:
            # self.limit = True
            pass
        else:
            # self.limit = True
            pass

    @api.model
    def create(self, vals):
        result = super(InheritSaleOrder, self).create(vals)
        print('AMT ==', result.amount_total, 'PLAF ==', result.partner_id.test)
        if result.partner_id.plafond > 0:
            compare_limit = result.amount_total + result.partner_id.reste_payer
            x = result.partner_id.credit_client - result.amount_total
            """calcul du réliquat et du crédit disponible"""
            if x <= 0:
                result.partner_id.test = result.partner_id.plafond - x
                result.partner_id.credit_client = 0
            else:
                result.partner_id.credit_client = x
            """Comparaison pour déterminer la limite de crédit"""
            if compare_limit > result.partner_id.plafond:
                raise ValidationError(
                    _("Vous ne pouvez pas créer des commandes pour ce client car sa limite de crédit est atteinte. "
                      "Veuillez effectuer un paiement avant de passer toute autre commande"))
            else:
                pass
        else:
            pass
        return result

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
