from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SyntheseSecii(models.Model):
    _name = 'secii.synthese'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Synthèse Secii'
    _rec_name = 'client'

    client = fields.Many2one('res.partner', string="Client", readonly=True)
    total_commandes = fields.Float(string='Total des commandes', compute='recherche_montant_facture')
    somme_payee = fields.Float(string='Somme Payée', compute="total_sommes_payees")
    reste = fields.Float(string='Solde Final', compute='get_reste')
    syn_id = fields.Char(string="ID")
    sync_id = fields.Char(string="ID")
    saleorder_ids = fields.One2many('sale.order', 'releve_client_id', string='Ventes')
    encaissement_ids = fields.One2many('secii.encaissement', 'rel_client_id', string='Encaissement')
    encaisse_ids = fields.One2many('secii.enc', 'enc_id', string='Relevé')
    sale_ids = fields.One2many('secii.vente', 'relv_client_id', string='Rélévé des ventes')
    message = fields.Text(string="Message")

    def printer_button(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'secii.rapport',
            'views': [[self.env.ref('account_secii.rapport_secii_form').id, 'form']],
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'name': 'Impression du rapport au format PDF',
        }

    def excel_button(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'secii.rapport',
            'views': [[self.env.ref('account_secii.rapport_secii_form_2').id, 'form']],
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'name': 'Impression du rapport au format Xlsx',
        }

    def fill_form(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "secii.synthese",
            "res_id": self.id,
            "views": [[self.env.ref('account_secii.synthese_secii_list').id, "tree"],
                      [self.env.ref('account_secii.synthese_secii_form').id, "form"]],
            'view_mode': 'tree, form',
            "name": "Relevé Client",
            'context': {'create': True},
        }

    def get_data_from_secii(self):
        data = {'id': self.id, 'client': self.client.id}
        return data

    def whatsapp_button(self):
        print('Send to Whatsapp work -_-')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'secii.whatsapp',
            'views': [[self.env.ref('account_secii.secii_whatsapp_send_msg').id, 'form']],
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_client': self.client.id},
            'name': 'Envoyer par Whatsapp',
        }

    def recherche_montant_facture(self):
        print('montant')
        for dt in self:
            dt.total_commandes = 0
            if dt.client:
                montant_cumule = self.env['sale.order'].sudo().search(
                    [('partner_id', '=', dt.client.id), ('state', 'in', ('sale', 'done')), ('is_prive', '=', 'True')]).mapped('amount_total')
                print('montant_cumule', montant_cumule)
                x = len(montant_cumule)
                print('x', x)
                for xz in montant_cumule:
                    dt.total_commandes += xz

    def total_sommes_payees(self):
        for val in self:
            # val.somme_payee = val.total_commandes - val.reste
            val.somme_payee = 0
            if val.client:
                cumul = self.env['account.secii'].sudo().search(
                    [('beneficiaire_is', '=', 'client'), ('beneficiaire_is_fournisseur', '=', val.client.id),
                     ('status', '=', 'valide'),
                     ('check_in_out', '=', 'entrer'), ('is_prive', '=', 'True')]).mapped('somme')
                #cumul = val.encaisse_ids.sudo().search(
                #    [('partenaire', '=', val.client.id), ('status', '=', 'paye')]).mapped('somme_paye')
                print('cumul', cumul)
                y = len(cumul)
                print('y', y)
                for csp in cumul:
                    val.somme_payee += csp

    def get_reste(self):
        for res in self:
            res.reste = res.total_commandes - res.somme_payee

    @api.model
    def default_get(self, fields_list):
        res = super(SyntheseSecii, self).default_get(fields_list)
        print('fields_list', fields_list, self)
        # vals = [(0, 0, {'name': value_1, 'date_order': value_2}),
        #         (0, 0, {'field_1': value_1, 'field_2': value_2})]
        # res.update({'your_o2m_field': vals})
        return res


class SeciiVente(models.Model):
    _name = 'secii.vente'
    _description = 'Rapport des ventes'

    relv_client_id = fields.Many2one('secii.synthese', string='Relevé Client')
    name = fields.Char(string='Numéro')
    date_order = fields.Date()
    partner_id = fields.Many2one('res.partner', string='Client')
    user_id = fields.Many2one('res.users', string='Vendeur')
    amount_total = fields.Float(string='Total des commandes')
    state = fields.Selection([('sale', 'Bon de Commandes'), ('done', 'Bloqué')])
    numero_bon = fields.Char(string="N° de Bon")

    def unlink(self):
        for val in self:
            print('Suppression Réussie')
        return super(SeciiVente, self).unlink()


class SeciiEnc(models.Model):
    _name = 'secii.enc'
    _description = 'Rapport des encaissements'
    _order = 'num_seq desc'

    enc_id = fields.Many2one('secii.synthese', string="Encaissement de :")
    date = fields.Date()
    num_seq = fields.Char()
    commercial = fields.Many2one('hr.employee')
    libele_op = fields.Char()
    partenaire = fields.Many2one('res.partner')
    montant_total = fields.Float('Total', digit=2)
    somme_paye = fields.Float('Somme Payée', digit=2)
    status = fields.Selection([('brouillon', 'BROUILLON'), ('paye', 'PAYE')])


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    releve_client_id = fields.Many2one('secii.synthese', string='Relevé Client')
    date_effective = fields.Datetime(string='Date Effective', required=True, index=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
                                     default=fields.Datetime.now,
                                     help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    numero_bon = fields.Char(string="N° de Bon")

    def action_confirm(self):
        """Fonction héritée permettant d'écrire les lignes de ventes et d'encaissements dans le relevé client"""
        res = super(SaleOrderInherit, self).action_confirm()

        for val in self:
            checking = self.env['secii.synthese'].sudo().search([('client', '=', val.partner_id.id)])
            print('checking =', checking)
            # check = checking.sale_ids.sudo().search([('partner_id', '=', val.partner_id.id), ('name', '=', val.name)])

            if val.is_prive:
                if checking:
                    print('checking existe')
                    action = {
                        'client': val.partner_id.id,
                        'syn_id': 'SALE' + str(val.id),
                        'sale_ids': [(0, 0, {
                            'name': val.name,
                            'date_order': val.date_effective,
                            'partner_id': val.partner_id.id,
                            'create_uid': val.create_uid.id,
                            'user_id': val.user_id.id,
                            'amount_total': val.amount_total,
                            'numero_bon': val.numero_bon,
                            'state': 'sale'
                        })]
                    }
                    checking.sudo().write(action)
                else:
                    print("checking n'existe pas")
                    action = {
                        'client': val.partner_id.id,
                        'syn_id': 'SALE' + str(val.id),
                        'sale_ids': [(0, 0, {
                            'name': val.name,
                            'date_order': val.date_effective,
                            'partner_id': val.partner_id.id,
                            'create_uid': val.create_uid.id,
                            'user_id': val.user_id.id,
                            'amount_total': val.amount_total,
                            'numero_bon': val.numero_bon,
                            'state': 'sale'
                        })]
                    }
                    checking.sudo().create(action)
            else:
                pass

        return res

    def action_cancel(self):
        """Fonction héritée permettant de supprimer les lignes de ventes et d'encaissements dans le relevé client"""
        res = super(SaleOrderInherit, self).action_cancel()
        for val in self:
            rt = self.env['secii.vente'].sudo().search(
                [('partner_id', '=', val.partner_id.id), ('name', '=', val.name)])
            for item in rt:
                if item:
                    item.sudo().unlink()
                else:
                    pass
        return res


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    retour = fields.Boolean()

    def button_confirm(self):
        """Fonction héritée permettant d'écrire les lignes de retour d'articles dans le relevé client"""
        res = super(PurchaseOrderInherit, self).button_confirm()
        for val in self:
            checking = self.env['secii.synthese'].sudo().search([('client', '=', val.partner_id.id)])
            if val.retour:
                if checking:
                    action = {
                        'client': val.partner_id.id,
                        'syn_id': 'SALE' + str(val.id),
                        'sale_ids': [(0, 0, {
                            'name': val.name,
                            'date_order': val.date_order,
                            'partner_id': val.partner_id.id,
                            'create_uid': val.create_uid.id,
                            'user_id': val.user_id.id,
                            'amount_total': -val.amount_total,
                            'state': 'sale'
                        })]
                    }
                    checking.sudo().write(action)
                else:
                    action = {
                        'client': val.partner_id.id,
                        'syn_id': 'SALE' + str(val.id),
                        'sale_ids': [(0, 0, {
                            'name': val.name,
                            'date_order': val.date_order,
                            'partner_id': val.partner_id.id,
                            'create_uid': val.create_uid.id,
                            'user_id': val.user_id.id,
                            'amount_total': -val.amount_total,
                            'state': 'sale'
                        })]
                    }
                    checking.sudo().create(action)
            else:
                pass
        return res

    def button_cancel(self):
        """Fonction héritée permettant de supprimer les lignes de retour d'articles dans le relevé client"""
        res = super(PurchaseOrderInherit, self).button_cancel()
        for val in self:
            rt = self.env['secii.vente'].sudo().search(
                [('partner_id', '=', val.partner_id.id), ('name', '=', val.name)])
            for item in rt:
                if item:
                    item.sudo().unlink()
                else:
                    pass
        return res


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Rapport des ventes'

    def action_create_payments(self):
        res = super(AccountPaymentRegister, self).action_create_payments()

        pay = self.env['account.move'].sudo().search([('payment_reference', '=', self.communication)])
        print('Pay is =', pay)

        search = self.env['account.secii'].sudo().search(
            [('beneficiaire_is_fournisseur', '=', pay.partner_id.id), ('date_prevue', '=', pay.invoice_date)])
        print('Search is =', search)
        print('Espèces', self.journal_id.name)

        for rec in self:
            if search:
                data = {
                    'create_date': rec.payment_date,
                    'date_prevue': pay.invoice_date,
                    'libele': 'Paiement de Facture ' + rec.communication,
                    'check_in_out': 'entrer',
                    'beneficiaire_is': 'client',
                    'beneficiaire_is_fournisseur': pay.partner_id.id,
                    # 'payment_with_employee': val.commercial.id,
                    # 'beneficiaire_employee': mov.commercial.id,
                    'borderau': pay.borderau,
                    'is_prive': False,
                    'somme': rec.amount,
                    'status': 'valide',
                }
                search.write(data)
            else:
                data = {
                    'create_date': pay.invoice_date,
                    'date_prevue': rec.payment_date,
                    'libele': 'Paiement de Facture ' + rec.communication,
                    'check_in_out': 'entrer',
                    'beneficiaire_is': 'client',
                    'beneficiaire_is_fournisseur': pay.partner_id.id,
                    # 'payment_with_employee': val.commercial.id,
                    # 'beneficiaire_employee': mov.commercial.id,
                    'borderau': pay.borderau,
                    'is_prive': False,
                    'somme': rec.amount,
                    'status': 'valide',
                }
                search.create(data)

        print('Envoi vers Caisse')

        return True


class SeciiEncaissementInherit(models.Model):
    _inherit = 'secii.encaissement'

    def put_draft(self):
        """Fonction héritée permettant de supprimer les lignes de retour d'articles dans le relevé client"""
        res = super(SeciiEncaissementInherit, self).put_draft()
        for val in self:
            rt = self.env['secii.enc'].sudo().search(
                [('partenaire', '=', val.partenaire.id), ('num_seq', '=', val.num_seq)])
            for item in rt:
                if item:
                    item.sudo().unlink()
                else:
                    pass
        return res
