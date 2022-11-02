from datetime import datetime
# from random import randint
#
import pytz
# from num2words import num2words

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SeciiEncaissement(models.Model):
    _name = 'secii.encaissement'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Nouvel Encaissement'
    _rec_name = 'num_seq'
    _order = 'create_date desc'

    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc


    def _get_actual_user(self):
        """Avoir l'ID de l'utilisateur connecté"""
        context = self._context
        current_uid = context.get('uid')
        user = self.env['hr.employee'].sudo().search([
            ('user_id', '=', current_uid)])
        # print(user.societe)
        return user.id

    partenaire = fields.Many2one('res.partner', string="Client", required=True)
    somme_paye = fields.Float(string="Somme Payée", digit=2)
    seq = fields.Char(string="N° de séquence")
    commercial = fields.Many2one('hr.employee', string="Commercial", index=True)  # , default=commercial_client
    date = fields.Date(string='Date ', default=_default_time_utc, tracking=True)
    note = fields.Text(string='Note', track_visibility='always')
    libele_op = fields.Text(string="Libellé d'opérations", default=' ')
    name = fields.Many2one('sale.order', string="N° de bon de commande")
    status = fields.Selection([('brouillon', 'BROUILLON'),
                               ('paye', 'PAYE'),
                               ('comptabilise', 'COMPTABILISE')],
                              default='brouillon')
    num_seq = fields.Char(string="N° Enc")
    attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Ajouter une pièce jointe:')
    commission = fields.Float(string="Commission", digit=2)
    montant_total = fields.Float(string="Total des commandes", group_operator=False)
    credit = fields.Float(string="Reste à payer")
    cumul = fields.Float(string="Cumul")
    instance = fields.Boolean(default=True, string="En Instance")
    is_enc = fields.Boolean()
    old_com = fields.Many2one('hr.employee', string="Ancien Commercial")
    recup = fields.Many2one('hr.employee', string="Récupérer par:", compute="_user_connected", store=True)
    # sh_rec = fields.Boolean()
    somme_total_paye = fields.Float()
    rel_client_id = fields.Many2one('secii.synthese', string='Relevé du Client')

    # @api.onchange('partenaire')
    # def compare_com_to_old(self):
    #     encaissement = self.env['secii.encaissement']
    #     cont = encaissement.sudo().search(
    #         ['&', '|', ('commercial', '=', self._get_actual_user()), ('commercial', '=', self.old_com.id),
    #          ('commercial', '=', self._get_actual_user())])
    #     print('Commerciaux', cont)

    # @api.depends('partenaire')
    # def get_partenaire(self):
    #     # all_com = []
    #     # com1 = self.env['hr.employee'].sudo().search([('user_id', '=', self._context.get('uid'))]).id
    #     # print(com1)
    #     # self.old_com = self.env['hr.employee'].sudo().search([('user_id', '=', self.partenaire.user_id_old)]).id
    #     # if com1 == self.old_com:
    #     #     self._get_actual_user()
    #     # else:
    #     #     all_com.append(com1)
    #     #     all_com.append(self.old_com.id)
    #     #     print('tous les commerciaux', all_com)
    #     # return all_com
    #     s_client = self.env['secii.encaissement'].sudo().search([('partenaire', '=', '')])

    @api.onchange('commercial')
    def _user_connected(self):
        print('Connected --//--')
        for val in self:
            val.recup = val._get_actual_user()

    def _default_account_journal_id(self):
        journal = self.env['account.journal'].sudo().search(
            [('code', '=', 'CAI'), ('company_id', '=', self.env.company.id)])
        return journal.id


    @api.onchange('partenaire')
    def onchange_partenaire_id(self):
        if self.partenaire.user_id:
            self.commercial = self.env['hr.employee'].sudo().search([('user_id', '=', self.partenaire.user_id.id)])
        else:
            self.commercial = False

    @api.onchange('instance')
    def onchange_instance(self):
        print('Onchange ------', 'ENC' + str(self._origin.id))
        stat = self.env['account.secii'].sudo().search([('seq_id', '=', 'ENC' + str(self._origin.id))])
        print('stat ------', stat)
        if stat:
            stat.write({"is_prive": self.instance})

    def unlink(self):
        """Empêche la suppression des données qui ont les statuts comptabilisé, payé et le statut != annulé dans mouvement de caisse"""
        for val in self:
            stat = self.env['account.secii'].sudo().search([('seq_id', '=', 'ENC' + str(val.id))])
            pay = self.env['account.payment'].sudo().search([('caisse_id', '=', 'PAI' + str(val.id))])
            print('Pay =', pay)
            if val.status != 'brouillon':
                raise ValidationError(
                    _("Suppression impossible, veuillez mettre l'opération en brouillon et l'annulé du coté de la caisse d'abord !"))

            else:
                if pay and stat:
                    print('Pay1 =', pay.state)
                    if stat.status == 'annule' and pay.state == 'draft':
                        print('Pay_1 =', pay.state)
                        stat.unlink()
                        pay.unlink()
                        return super(SeciiEncaissement, self).unlink()
                    else:
                        raise ValidationError(
                            _("Suppression impossible, veuillez mettre l'opération en brouillon et l'annulé du coté de la caisse d'abord !"))
                elif pay:
                    print('Pay2 =', pay)
                    if pay.state == 'draft':
                        pay.unlink()
                        return super(SeciiEncaissement, self).unlink()
                    else:
                        raise ValidationError(
                            _("Suppression impossible, veuillez mettre l'opération en brouillon et l'annulé du coté de la caisse d'abord !"))
                elif stat:
                    print('sshyshsh')
                    if stat.status == 'annule':
                        print('annnnnnule')
                        stat.unlink()
                        return super(SeciiEncaissement, self).unlink()
                    else:
                        raise ValidationError(
                            _("Suppression impossible, veuillez mettre l'opération en brouillon et l'annulé du coté de la caisse d'abord !"))
                else:
                    print('fin =', stat.status)
                    return super(SeciiEncaissement, self).unlink()

    @api.onchange('somme_paye')
    def get_rest_topaye(self):
        """calcul du reste à payer"""
        for record in self:
            total_cumul = 0
            cumul = self.env['secii.encaissement'].sudo().search(
                [('partenaire', '=', record.partenaire.id)]).mapped('somme_paye')
            print("pppppoooooooooooooooo", cumul)
            print("partenaire =", record.partenaire.id)
            for x in cumul:
                total_cumul += x
            record.cumul = total_cumul + record.somme_paye
            print(record.somme_paye)
            print("newwwww", record.somme_total_paye)
            print("hhhhhhhhhhhhhh", record.cumul)
            print("pppppppppppppp", record.montant_total)
            if record.montant_total == 0:
                record.credit = 0
            else:
                if record.somme_paye < 0:
                    raise ValidationError(
                        _("La somme a payé ne peut être une valeur négative !"))
                elif record.cumul > record.montant_total:
                    raise ValidationError(
                        _("La somme a payé ne peut excéder le montant total des commandes !"))
                else:
                    print('==== reste à payer ====')
                    record.credit = record.montant_total - record.cumul

    @api.onchange('somme_paye')
    def calcul_reste(self):
        """obtenir le reste à payer en fonction de la somme payée"""
        self.get_rest_topaye()

    @api.onchange('partenaire')
    def recherche_montant_facture(self):
        """Recupération des montants en fonction du client"""
        print('montant')
        for dt in self:
            dt.montant_total = 0
            if dt.partenaire:
                montant_cumule = self.env['sale.order'].sudo().search(
                    [('partner_id', '=', dt.partenaire.id), ('state', 'in', ('sale', 'done')), ('is_prive', '=', 'True')]).mapped(
                    'amount_total')
                print('montant_cumule', montant_cumule)
                x = len(montant_cumule)
                print('x', x)
                for xz in montant_cumule:
                    dt.montant_total += xz
            dt.get_rest_topaye()


    def open_caisse(self):
        """Fonction pour ouvrir la caisse et acceder à l'encaissement déjà crée"""
        action = {'type': 'ir.actions.act_window',
                  'name': 'Mouvement de Caisse',
                  'view_mode': 'tree,form',
                  'view_type': 'form',
                  'res_model': 'account.secii',
                  'view_id': False,
                  }

        domain = ([('seq_id', '=', 'ENC' + str(self.id))])
        action['domain'] = domain
        return action


    def put_validate(self):
        """Fonction permettant de payer l'encaissement et qui crée une ligne dans la caisse"""
        print('self ------', self)
        self.status = 'paye'
        for val in self:
            print('ENC' + str(val.id))
            val.message_post(body="statut ==> Payé")
            if val.somme_paye < 0:
                raise ValidationError(_('Le montant à payer doit être supérieur à zéro'))
            duplicate = self.env['account.secii'].sudo().search([('seq_id', '=', 'ENC' + str(val.id))])
            print('duplicate', duplicate)
            if duplicate:
                invoice_vals = {
                    'create_date': val.date,
                    'seq_id': 'ENC' + str(val.id),
                    'libele': val.libele_op + " N° de l'encaissement " + str(val.num_seq),
                    'check_in_out': 'entrer',
                    'enc': True,
                    'beneficiaire_is': 'client',
                    'beneficiaire_is_fournisseur': val.partenaire.id,
                    'payment_with_employee': val.commercial.id,
                    # 'beneficiaire_employee': mov.commercial.id,
                    'is_prive': val.instance,
                    'somme': val.somme_paye,
                    'status': 'valide',
                    'note': val.note
                }
                duplicate.write(invoice_vals)
            else:
                invoice_vals = {
                    'create_date': val.date,
                    'seq_id': 'ENC' + str(val.id),
                    'libele': val.libele_op + " N° de l'encaissement " + val.num_seq,
                    'check_in_out': 'entrer',
                    'enc': True,
                    'beneficiaire_is': 'client',
                    'beneficiaire_is_fournisseur': val.partenaire.id,
                    'payment_with_employee': val.commercial.id,
                    # 'beneficiaire_employee': mov.commercial.id,
                    'is_prive': val.instance,
                    'somme': val.somme_paye,
                    'status': 'valide',
                    'note': val.note
                }
                result = self.env['account.secii'].sudo().create(invoice_vals)
                print('result =', result)
            self.creation_rapport()
        return True

    def put_draft(self):
        self.status = 'brouillon'
        # # facture = self.env['account.move'].sudo().search([('id', '=', self.facture_id)])
        # # if facture.state == 'posted':
        # #     raise ValidationError(_('Vous ne pouvez pas remettre en brouillon une opération déjà comptabilisée'))
        # # else:
        # #     facture.unlink()
        # #     self.env['account.payment'].sudo().search([('id', '=', self.payment_id)]).unlink()
        for val in self:
            val.message_post(body="statut ==> Brouillon")
        return True


    def comptabilise_operation(self):
        """Écriture dans la table account.secii"""
        for payment in self:
            print('88888888888888888', payment.id)
            if payment.status != 'comptabilise':
                payment.status = 'comptabilise'
            duplicate = self.env['account.payment'].sudo().search([('caisse_id', '=', 'PAI' + str(payment.id))])
            print('duplicate =', duplicate)
            if duplicate:
                paired_payment = {
                    'type_caisse': 'comptable',
                    'date': payment.date,
                    'caisse_id': 'PAI' + str(payment.id),
                    'ref': payment.num_seq,
                    # 'payment_method_line_id': 'manuel',
                    'payment_type': 'inbound',
                    'amount': payment.somme_paye,
                    'partner_id': payment.partenaire.id,
                    # 'amount': abs(payment.somme) + (amount_tax * abs(payment.somme)) / 100,
                }
                duplicate.write(paired_payment)
            else:
                paired_payment = {
                    'type_caisse': 'manager',
                    'date': payment.date,
                    'caisse_id': 'PAI' + str(payment.id),
                    # 'ref': payment.name.name,
                    # 'payment_method_line_id': 'manuel',
                    'payment_type': 'inbound',
                    'journal_id': payment._default_account_journal_id(),
                    'amount': payment.somme_paye,
                    'move_id': None,
                    'partner_id': payment.partenaire.id,
                    'partner_type': 'customer'
                    # 'amount': abs(payment.somme) + (amount_tax * abs(payment.somme)) / 100,
                }
                # paired_payment.update({'partner_type': 'customer'})
                resul = self.env['account.payment'].sudo().create(paired_payment)
                resul.action_post()  # créer le relévé dans account.bank.statement

        for val in self:
            val.message_post(body="statut ==> Comptabilisé")

        return True

    def open_payment(self):
        action = {'type': 'ir.actions.act_window', 'name': 'Paiements', 'view_mode': 'tree,form', 'view_type': 'form',
                  'res_model': 'account.payment', 'view_id': False}

    def open_facture(self):
        action = {'type': 'ir.actions.act_window', 'name': 'Factures', 'view_mode': 'tree,form', 'view_type': 'form',
                  'res_model': 'account.move', 'view_id': False}
        # if self.beneficiaire_is == 'fournisseur':
        #     print('*********************')
        #     domain = ([('caisse_id', '=', 'MOUV' + str(self.id)), ('move_type', '=', 'in_invoice')])
        #     action['domain'] = domain
        # elif self.beneficiaire_is == 'client':
        #     print('......................')
        #     domain = ([('caisse_id', '=', 'MOUV' + str(self.id)), ('move_type', '=', 'out_invoice')])
        #     action['domain'] = domain
        # return action

    def calcul_somme_paye(self):
        """Somme de toutes les sommes payées"""
        for record in self:
            total_cumul = 0
            cumul = self.env['secii.encaissement'].sudo().search(
                [('partenaire', '=', record.partenaire.id),
                 ('status', 'in', ('paye', 'brouillon', 'comptabilise'))]).mapped('somme_paye')
            print("pppppoooooooooooooooo", cumul)
            for x in cumul:
                total_cumul += x
            record.cumul = total_cumul + record.somme_paye
            record.somme_total_paye = record.cumul
            return record.somme_total_paye

    def creation_rapport(self):
        print('creation du rapport')
        for val in self:
            print('--:--')

            # verification si les données existent dans le rapport
            checking = self.env['secii.synthese'].sudo().search([('client', '=', val.partenaire.id)])
            print('checking =', checking)

            # verification si le client a déjà des encaissements payés
            check = self.env['secii.encaissement'].sudo().search(
                [('partenaire', '=', val.partenaire.id), ('status', '=', 'paye')])
            print('check =', check)

            x = len(check)
            print(x)

            # si les données existent
            if val.instance:
                if checking:
                    print('checking existe')
                    # les valeurs de
                    action = {
                        'client': val.partenaire.id,
                        'sync_id': 'ENC' + str(val.id),
                        'encaisse_ids': [(0, 0, {
                            'date': val.date,
                            'num_seq': val.num_seq,
                            # 'recup': val.commercial.id,
                            'commercial': val.commercial.id,
                            'libele_op': val.libele_op,
                            'partenaire': val.partenaire.id,
                            'montant_total': val.montant_total,
                            'somme_paye': val.somme_paye,
                            'status': val.status,
                        })],
                    }
                    checking.sudo().write(action)
                else:
                    action = {
                        'client': val.partenaire.id,
                        'sync_id': 'ENC' + str(val.id),
                        'encaisse_ids': [(0, 0, {
                            'date': val.date,
                            'num_seq': val.num_seq,
                            # 'recup': val.commercial.id,
                            'commercial': val.commercial.id,
                            'libele_op': val.libele_op,
                            'partenaire': val.partenaire.id,
                            'montant_total': val.montant_total,
                            'somme_paye': val.somme_paye,
                            'status': val.status,
                        })],
                    }
                    checking.sudo().create(action)
            else:
                pass

    @api.model
    def create(self, vals):
        vals['num_seq'] = self.env['ir.sequence'].next_by_code('secii.encaissement')
        # for val in self:
        #     self.message_post(body="Nouvel encaissement crée par " + str(val.recup.name))
        # action =
        result = super(SeciiEncaissement, self).create(vals)
        return result

    def redirect_commercial(self):
        print('Début')
        """Récupération de l'employee connectée"""
        user = self.env['hr.employee'].sudo().search([
            ('user_id', '=', self._context.get('uid'))])
        print('Us', user, user.user_id.id)

        """Recherche de l'employee connectée en tant que vendeur dans les contacts"""
        res = self.env['res.partner'].sudo().search([('user_id', '=', user.user_id.id)])
        print('Res', res)

        """Action permettant de trouver l'ID de la vue"""
        # action = self.env['ir.actions.act_window']._for_xml_id("account_secii.changement_commerciaux_secii_action")
        # action['context'] = dict(ast.literal_eval(action.get('context')))

        """Recherche dans Res Partner """
        for elt in res:
            print('elt =', elt)
            # rec = self.env['hr.employee'].sudo().search([('user_id', '=', elt.user_id_old)]).id
            if elt.user_id_old:
                print('Le commercial a été changé')
                # enc = self.env['secii.encaissement'].sudo().search([('commercial', 'in', (elt.user_id_old, user.id))])
                # print('Enc ===', enc)
                com = [elt.user_id_old, user.id]
            else:
                print("Le commercial n'a pas été changé")
                com = user.id
        return com
