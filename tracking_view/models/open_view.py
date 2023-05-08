from odoo import fields, models, api, _


class TrackingInstancePartnerInherit(models.Model):
    _inherit = 'tracking.partner'

    def open_model_views(self):
        """Fonction pour ouvrir les différentes vues en fonction de leurs provenances"""
        print('Test Ouverture model', self.reference, self.designation)
        design = self.designation

        action = {
            'name': _(''),
            'type': 'ir.actions.act_window',
            'view_type': 'list',
            'view_mode': 'list',
            'target': 'new',
            'context': {'create': False, 'export_xlsx': False},
        }

        if design == 'Encaissement':
            print('Encaissement')
            action.update({'name': design, 'res_model': 'secii.encaissement',
                           'views': [(self.env.ref('account_secii.encaissement_commerciaux_list').id, 'list')],
                           'domain': [('num_seq', '=', str(self.reference))]})

        elif design in ('Facture Achat', 'Avoir fournisseur', 'Avoir Client', 'Facture Vente'):
            print('Facture')
            action.update({'name': design, 'res_model': 'account.move',
                           'views': [(self.env.ref('account.view_invoice_tree').id, 'list')],
                           'domain': [('name', '=', str(self.reference)), ('id', '=', self.move_id.id)]})

        elif design == 'Pièces comptables':
            print('Pièces comptables')
            action.update({'name': design, 'res_model': 'account.move.line',
                           'views': [(self.env.ref('account.view_move_tree').id, 'list')],
                           'domain': [('name', '=', str(self.reference)), ('id', '=', self.move_id.id)]})

        elif design == 'Paiement':
            print('Paiement')
            action.update({'name': design, 'res_model': 'account.payment',
                           'views': [(self.env.ref('account.view_account_payment_tree').id, 'list')],
                           'domain': [('name', '=', str(self.reference)), ('id', '=', self.payment_id.id)]})

        elif design == 'Vente':
            print('Vente')
            action.update({'name': design, 'res_model': 'sale.order',
                           'views': [(self.env.ref('sale.view_quotation_tree').id, 'list')],
                           'domain': [('name', '=', str(self.reference))]})

        elif design in ('Achat', 'Retour Achat'):
            print('Achat')
            action.update({'name': design, 'res_model': 'purchase.order',
                           'views': [(self.env.ref('purchase.purchase_order_kpis_tree').id, 'list')],
                           'domain': [('name', '=', str(self.reference)), ('id', '=', self.purchase_id.id)]})
        return action
