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
    retour = fields.Float(string='Retour de marchandises', compute="total_sommes_payees")
    reste = fields.Float(string='Solde Final', compute='get_reste')
    syn_id = fields.Char(string="ID")
    sync_id = fields.Char(string="ID")
    saleorder_ids = fields.One2many('sale.order', 'releve_client_id', string='Ventes')
    encaissement_ids = fields.One2many('secii.encaissement', 'rel_client_id', string='Encaissement')
    encaisse_ids = fields.One2many('secii.enc', 'enc_id', string='Relevé')
    sale_ids = fields.One2many('secii.vente', 'relv_client_id', string='Rélévé des ventes')
    message = fields.Text(string="Message")
    active = fields.Boolean(string="Archivé", default=True)
    commune = fields.Selection(related='client.commune', store=True)

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
                    [('partner_id', '=', dt.client.id), ('state', 'in', ('sale', 'done')),
                     ('is_prive', '=', 'True')]).mapped('amount_total')
                print('montant_cumule', montant_cumule)
                x = len(montant_cumule)
                print('x', x)
                for xz in montant_cumule:
                    dt.total_commandes += xz

    def total_sommes_payees(self):
        for val in self:
            # val.somme_payee = val.total_commandes - val.reste
            val.somme_payee = 0
            val.retour = 0
            if val.client:
                cumul = self.env['account.secii'].sudo().search(
                    [('beneficiaire_is', '=', 'client'), ('beneficiaire_is_fournisseur', '=', val.client.id),
                     ('status', '=', 'valide'),
                     ('check_in_out', '=', 'entrer'), ('is_prive', '=', 'True')]).mapped('somme')

                retour_marchandise = self.env['purchase.order'].sudo().search([('partner_id', '=', val.client.id),
                                                                               ('state', '=', 'purchase'),
                                                                               ('retour', '=', True),
                                                                               ('is_prive', '=', True)]).mapped(
                    'amount_total')
                # cumul = val.encaisse_ids.sudo().search(
                #    [('partenaire', '=', val.client.id), ('status', '=', 'paye')]).mapped('somme_paye')
                print('cumul', cumul)
                print('retour de marchandise', retour_marchandise)
                y = len(cumul)
                print('y', y)
                for csp in cumul:
                    val.somme_payee += csp
                for rtm in retour_marchandise:
                    val.retour += rtm

    def get_reste(self):
        for res in self:
            res.reste = res.total_commandes - res.somme_payee - res.retour

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
    state = fields.Selection([('sale', 'Bon de Commandes'), ('done', 'Bloqué'), ('purchase', 'Achat')])
    numero_bon = fields.Char(string="N° de Bon")

    def unlink(self):
        for val in self:
            print('Suppression Réussie')
        return super(SeciiVente, self).unlink()

    def namelink(self):
        """Fonction pour ouvrir la caisse et acceder à l'encaissement déjà crée"""
        action = {'type': 'ir.actions.act_window',
                  'name': 'Devis',
                  'view_mode': 'tree,form',
                  'view_type': 'form',
                  'res_model': 'sale.order',
                  'view_id': False,
                  }

        domain = ([('name', '=', self.name)])
        action['domain'] = domain
        return action


class SeciiEnc(models.Model):
    _name = 'secii.enc'
    _description = 'Rapport des encaissements'
    _order = 'num_seq desc'

    enc_id = fields.Many2one('secii.synthese', string="Encaissement de :")
    date = fields.Date()
    date_effective = fields.Datetime()
    num_seq = fields.Char()
    commercial = fields.Many2one('hr.employee')
    libele_op = fields.Char()
    partenaire = fields.Many2one('res.partner')
    montant_total = fields.Float('Total', digit=2)
    somme_paye = fields.Float('Somme Payée', digit=2)
    credit_client = fields.Float('Crédit Client', digit=0)
    status = fields.Selection([('brouillon', 'BROUILLON'), ('paye', 'PAYE')])

    def unlink(self):
        for val in self:
            print('Suppression Encaissement Réussie')
        return super(SeciiEnc, self).unlink()

    def recup_enc_rel_client(self):
        print('ENC')

    def enclink(self):
        """Fonction pour ouvrir la caisse et acceder à l'encaissement déjà crée"""
        action = {'type': 'ir.actions.act_window',
                  'name': 'Encaissement',
                  'view_mode': 'tree,form',
                  'view_type': 'form',
                  'res_model': 'secii.encaissement',
                  'view_id': False,
                  }

        domain = ([('num_seq', '=', self.num_seq)])
        action['domain'] = domain
        return action


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    releve_client_id = fields.Many2one('secii.synthese', string='Relevé Client')
    name_rel = fields.Many2one('secii.vente', string="Name")
    date_effective = fields.Datetime(string='Date Effective', required=True, index=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
                                     default=fields.Datetime.now,
                                     help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    numero_bon = fields.Char(string="N° de Bon")
    mc = fields.Float(string='Montant')
    suivi_up = fields.Boolean()

    def action_confirm(self):
        """Fonction héritée permettant d'écrire les lignes de ventes et d'encaissements dans le relevé client"""
        res = super(SaleOrderInherit, self).action_confirm()

        for val in self:
            checking = self.env['secii.synthese'].sudo().search([('client', '=', val.partner_id.id)])
            print('checking =', checking)
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
                            'state': 'sale'})]
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
                            'state': 'sale'})]
                    }
                    checking.sudo().create(action)
            else:
                pass

        return res

    def recup_sale_rel_client(self):
        res = self.env['sale.order'].sudo().search([('state', '=', 'sale'), ('is_prive', '=', True)])
        vente = self.name_rel.sudo()
        for so in res:
            """Récupération de tous les achats avec l'état sale et en instance"""
            vt = vente.search([('name', '=', so.name), ('partner_id', '=', so.partner_id.id)])
            for elt in vt:
                elt.update({'amount_total': so.amount_total})
        self.suivi_up = True

    def recup_all(self):
        print('Factures', '+')
        facture = self.env['account.move'].sudo().search([('state', '=', 'posted')])
        for fct in facture:
            if fct.move_type in ['in_invoice', 'in_refund', 'out_refund', 'out_invoice']:
                action = {
                    'partner': fct.partner_id.id,
                    'reference': fct.name,
                    'designation': 'Facture Achat',
                    'libele_op': 'Facture ' + fct.name,
                    'date': fct.create_date,
                    'move_id': fct.id,
                    'amount_currency': fct.amount_total
                }
                if fct.move_type == 'in_refund':
                    print('Avoir fournisseur', '-')
                    action.update({
                        'designation': 'Avoir fournisseur',
                        'partner_type': 'vendor',
                        'amount_currency': - fct.amount_total
                    })
                elif fct.move_type == 'out_refund':
                    print('Avoir Client', '-')
                    action.update({
                        'designation': 'Avoir Client',
                        'partner_type': 'customer',
                        'amount_currency': - fct.amount_total
                    })
                elif fct.move_type == 'in_invoice':
                    action.update(
                        {'partner_type': 'vendor'}
                    )
                elif fct.move_type == 'out_invoice':
                    action.update(
                        {'partner_type': 'customer',
                         'designation': 'Facture Vente'}
                    )
                tracking = self.env['tracking.partner'].sudo().search([('move_id', '=', fct.id)])
                if tracking:
                    tracking.sudo().write(action)
                else:
                    # action.update({
                    #     'not_instance': True
                    # })
                    tracking.sudo().create(action)

        print('Pièces comptables', '+')
        p_comptable = self.env['account.move.line'].sudo().search(
            [('parent_state', '=', 'posted'), ('name', '=', 'SOLDE INITIAL')])
        for pc in p_comptable:
            action = {
                'partner': pc.partner_id.id,
                'reference': pc.move_name,
                'designation': 'Pièces comptables',
                'libele_op': pc.name,
                'date': pc.date,
                'payment_ref': str(pc.id) + 'PC',
                'partner_type': 'customer',
                'not_instance': True
            }
            if pc.account_id.code == str(411100):
                action.update({
                    # 'credit': val.credit,
                    'amount_currency': pc.debit
                    # 'amount_cf': val.credit,

                })
            tracking = self.env['tracking.partner'].sudo().search([('payment_ref', '=', str(pc.id) + 'PC')])
            if tracking:
                tracking.sudo().write(action)
            else:
                tracking.sudo().create(action)

        print('Paiements', '-')
        paie = self.env['account.payment'].sudo().search([('state', '=', 'posted')])
        for elt in paie:
            if elt.partner_type in ['supplier', 'customer']:
                action = {
                    'partner': elt.partner_id.id,
                    'reference': elt.name,
                    'designation': 'Paiement',
                    'libele_op': 'Paiement ' + elt.name,
                    'date': elt.create_date,
                    'payment_id': elt.id,
                    'partner_type': elt.partner_type,
                    'amount_currency': - elt.amount
                }
                tracking = self.env['tracking.partner'].sudo().search([('payment_id', '=', elt.id)])
                if elt.partner_type == 'supplier':
                    action.update({'partner_type': 'vendor'})
                elif elt.payment_type == 'customer':
                    action.update({'partner_type': 'customer'})
                if tracking:
                    tracking.write(action)
                else:
                    action.update({
                        'not_instance': True
                    })
                    if elt.journal_id.type == 'bank':
                        action.update({'payment_method': 'bank'})
                    elif elt.journal_id.type == 'cash':
                        action.update({'payment_method': 'espece'})
                    tracking.create(action)

        print('Ventes', '+')
        vente = self.env['sale.order'].sudo().search([('is_prive', '=', True), ('state', '=', 'sale')])
        for vt in vente:
            if vt:
                tracking = self.env['tracking.partner'].sudo().search([('purchase_ref', '=', str(vt.id) + 'VEN')])
                action = {
                    'partner': vt.partner_id.id,
                    'reference': vt.name,
                    'designation': 'Vente',
                    'libele_op': ' ',
                    'date': vt.date_order,
                    'purchase_ref': str(vt.id) + 'VEN',
                    'partner_type': 'customer',
                    'amount_currency': vt.amount_total,
                }
                if tracking:
                    tracking.write(action)
                else:
                    tracking.create(action)
            else:
                pass

        print('Achats', '+')
        achat = self.env['purchase.order'].sudo().search([('state', '=', 'purchase')])
        for ach in achat:
            if ach.is_prive:
                action = {
                    'partner': ach.partner_id.id,
                    'reference': ach.name,
                    'designation': 'Achat',
                    'date': ach.create_date,
                    'purchase_ref': str(ach.id) + 'ACH',
                    'partner_type': 'vendor',
                    'purchase_id': ach.id,
                    'amount_currency': ach.amount_total,
                }
                if ach.retour:
                    print("Retour d'Achats", '-')
                    action.update({
                        'amount_currency': - ach.amount_total,
                        'partner_type': 'customer',
                        'designation': "Retour Achat",
                    })
                tracking = self.env['tracking.partner'].sudo().search([('purchase_ref', '=', str(ach.id) + 'ACH')])
                if tracking:
                    tracking.sudo().write(action)
                else:
                    tracking.sudo().create(action)
            else:
                pass

        print('Encaissements', '-')
        encaiss = self.env['secii.encaissement'].sudo().search([('instance', '=', True), ('status', '=', 'paye')])
        for enc in encaiss:
            if enc:
                print('ENC88888', enc)
                tracking = self.env['tracking.partner'].sudo().search([('purchase_ref', '=', str(enc.id) + 'ENC')])
                print('TRK88888', tracking)
                action = {
                    'partner': enc.partenaire.id,
                    'reference': enc.num_seq,
                    'designation': 'Encaissement',
                    'libele_op': enc.libele_op,
                    'date': enc.date,
                    'purchase_ref': str(enc.id) + 'ENC',
                    'partner_type': 'customer',
                    'amount_currency': - enc.somme_paye,
                }
                if tracking:
                    tracking.write(action)
                else:
                    tracking.create(action)
            else:
                pass

    def action_cancel(self):
        """Fonction héritée permettant de supprimer les lignes de ventes et d'encaissements dans le relevé client"""
        res = super(SaleOrderInherit, self).action_cancel()
        vente = self.name_rel.sudo()
        for val in self:
            rt = vente.search([('partner_id', '=', val.partner_id.id), ('name', '=', val.name)])
            for item in rt:
                if item:
                    item.sudo().unlink()
                else:
                    pass
        return res


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    retour = fields.Boolean()
    suivi_up = fields.Boolean()

    def button_confirm(self):
        """Fonction héritée permettant d'écrire les lignes de retour d'articles dans le relevé client"""
        res = super(PurchaseOrderInherit, self).button_confirm()
        print('TEst')
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
                            'state': 'purchase'
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
                            'state': 'purchase'
                        })]
                    }
                    checking.sudo().create(action)
            else:
                pass
        return res

    def recup_purchase(self):
        res = self.env['purchase.order'].sudo().search([('state', '=', 'purchase'), ('retour', '=', True), ('is_prive', '=', True)])
        print('test')
        for po in res:
            """Récupération de tous les achats avec l'état purchase et retour True avec en instance"""
            vt = self.env['secii.vente'].sudo().search(
                [('name', '=', po.name), ('partner_id', '=', po.partner_id.id)])
            for elt in vt:
                elt.update({'state': 'purchase', 'amount_total': -po.amount_total})
        self.suivi_up = True

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
