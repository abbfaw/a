from odoo import fields, models, api, _


class TrackingInstancePartnerInherit(models.Model):
    _inherit = 'tracking.partner'

    def open_model_views(self):
        """Fonction pour ouvrir les différentes vues en fonction de leurs provenances"""
        print('Test Ouverture model', self.reference, self.designation)
        design = self.designation

        if design == 'Encaissement':
            print('Encaissement')
            action = self.env['ir.actions.act_window']._for_xml_id('account_secii.encaissement_secii_action')
            action['domain'] = [('num_seq', '=', str(self.reference))]

        elif design in ('Facture Achat', 'Avoir fournisseur', 'Avoir Client', 'Facture Vente'):
            print('Facture')
            action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_receipt_type')
            action['domain'] = [('name', '=', str(self.reference)), ('id', '=', self.move_id.id)]

        elif design == 'Pièces comptables':
            print('Pièces comptables')
            action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_journal_line')
            action['domain'] = [('name', '=', str(self.reference)), ('id', '=', self.move_id.id)]

        elif design == 'Paiement':
            print('Paiement')
            action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_payments')
            action['domain'] = [('name', '=', str(self.reference)), ('id', '=', self.payment_id.id)]

        elif design == 'Vente':
            print('Vente')
            action = self.env['ir.actions.act_window']._for_xml_id('sale.action_orders')
            action['domain'] = [('name', '=', str(self.reference))]

        elif design in ('Achat', 'Retour Achat'):
            print('Achat')
            action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_rfq')
            action['domain'] = [('name', '=', str(self.reference))]

        return action
