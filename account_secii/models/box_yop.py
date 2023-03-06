from datetime import datetime

import pytz
from num2words import num2words

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class CaisseSecondaire(models.Model):
    _name = 'account.yop'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'sequence.mixin']
    _order = 'name DESC, create_date DESC'
    _description = 'mouvement caisse yop'
    _check_company_auto = True

    @api.model
    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    def _default_account_journal_id(self):
        journal = self.env['account.journal'].search([('code', '=', 'CAIY'), ('company_id', '=', self.env.company.id)])
        return journal.id

    create_date = fields.Date(string='Date de création:', default=_default_time_utc, readonly=True)
    date = fields.Date(string='Date ', default=_default_time_utc)
    libele = fields.Text(string='Libellé:', default='aucun')
    num_facture = fields.Char(string="Numéro facture:", require=True)
    nature_payment = fields.Selection([('espece', 'Espèce'), ('autre', 'Autre')], default='espece')
    payment_with = fields.Selection(
        [('employee', 'Employé'), ('client', 'Client'), ('fournisseur', 'Fournisseur'), ('autre', 'Autre')],
        "Par l’intermédiaire de:", default='employee')
    payment_with_employee = fields.Many2one('hr.employee', string='Employé:', check_company=True)
    payment_with_fourn = fields.Many2one('res.partner', string='Fournisseur:', check_company=True)
    payment_with_client = fields.Many2one('res.partner', string='Client:', check_company=True)
    payment_with_other = fields.Many2one('res.partner', string='Nom :', check_company=True)
    beneficiaire_is = fields.Selection(
        [('employee', 'Employé'), ('client', 'Client'), ('fournisseur', 'Fournisseur'), ('autre', 'Autre')],
        "Partenaire:", default='employee')
    beneficiaire_employee = fields.Many2one('hr.employee', string='Employé Bénéficiaire:', check_company=True)
    beneficiaire_is_fournisseur = fields.Many2one('res.partner', string='Fournisseur Bénéficiaire:', check_company=True)
    check_in_out = fields.Selection(
        [('entrer', 'Entrée'), ('sortie', 'Sortie'), ('transfer', 'Transfert vers Banque')],
        'Entrée/Sortie', default='sortie')
    somme = fields.Float(string='Somme:')
    update = fields.Datetime(string='Mise à jour le:')
    update_by = fields.Many2one('res.users', string='Mise à jour par:')
    visibility = fields.Selection([('0', 'Oui'), ('1', 'Non')],
                                  "à ne pas déclarer ?", default='1')
    name = fields.Char(string="N° de bon")
    chantier_id = fields.Many2one('account.analytic.account', string="Projet",
                                  check_company=True)  # , 'agentis_office_id'
    etat = fields.Boolean(string='etat')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=False, store=True,
                                  default=lambda self: self.env.company.currency_id)
    solde = fields.Monetary(string='Somme', compute='get_solde', store=True, currency_field='currency_id')
    somme_in = fields.Float(string=' Somme', compute='get_somme_in')
    somme_out = fields.Float(string='Somme', compute='get_somme_out')
    is_create = fields.Boolean(string='est crée')
    insible_somme = fields.Boolean(string='somme visble ou non')

    donne_a_client = fields.Many2one('res.partner', string='Donné à :', check_company=True)
    donne_a_employe = fields.Many2one('hr.employee', string='Donné à :', check_company=True)
    status = fields.Selection([('brouillon', 'BROUILLONS'), ('attente', 'EN ATTENTE'), ('valide', 'VALIDE'),
                               ('comptabilise', 'COMPTABILISE')],
                              default='brouillon')
    company_id = fields.Many2one('res.company', string='Société:', required=True, default=lambda self: self.env.company)
    product_id = fields.Many2one('product.product', 'Product', required=False, default=0)
    journal_id = fields.Many2one('account.journal', string='Journal comptable:', default=_default_account_journal_id,
                                 check_company=True)
    tax_id = fields.Many2one('account.tax', string='Taxe:')
    facture_id = fields.Integer(string='id facture')
    payment_id = fields.Integer(string='id payment')
    date_prevue = fields.Date(string='Date Effective:', default=_default_time_utc)
    file = fields.Binary(string="Fichier")
    file_name = fields.Char(string='nom fichier')
    type_caisse = fields.Selection([('dga', 'DGA'), ('manager', 'Office manager'), ('comptable', 'Comptable')],
                                   'Type de caisse')
    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='account_yop_id',
        string='Ajouter une pièce jointe:')
    bank_reception = fields.Many2one('agentis.bank', string='Banque Emettrice')
    methode_payment = fields.Selection(
        [('virement', 'Virement'), ('versement', 'Versement'), ('misedispo', 'Mise à Disposition'),
         ('chequebarre', 'Chèque Barré'), ('chequenonbarre', 'Chèque Non Barré'), ('espece', 'Espèce')],
        "Méthode de paiément", default='virement')
    total_somme = fields.Float(string='somme total', compute='get_total_somme')
    somme_lettre = fields.Char(string='Somme lettre')
    type_operation = fields.Selection([('local', 'Local'), ('inter', 'International')], "Type d'operation",
                                      default='local')
    origin_fond = fields.Many2many('origin.fond', store=True, string='origine des fonds', readonly=False)
    borderau = fields.Boolean(string='Borderau de livraison')
    num_borderau = fields.Char(string='N° Borderau')
    num_contrat = fields.Many2one('agentis.contrat', string='Numéro du contrat')
    somme_char = fields.Char(string='somme en caractere', compute='get_somme_char')
    cree_facture = fields.Boolean(string='Créer une facture')

    # /----------Champs Modifiés--------------/
    note = fields.Text(string='Note', track_visibility='always')
    facture = fields.Boolean(string='Crée une Facture ?')
    amount_facture = fields.Integer(string='somme facture', track_visibility='always')
    exist_facture_select = fields.Many2one('account.move', string='Selectionner la facture')
    exist_facture = fields.Boolean(string='Facture existante ?')
    hide_boolean = fields.Boolean(string='Cacher fact et pay', default=False)
    maroc = fields.Boolean(string='MAROC')
    company_create = fields.Many2one('res.company', string='Créer dans:', track_visibility='always',
                                     default=lambda self: self.env.company)
    caisse_id = fields.Char(string='Identifiant Caisse')
    no_see_dga = fields.Boolean(string='A caché', help='permert de caché les lignes privées consolidées')
    total_facture_with_tax = fields.Float(string='Montant avec taxe', compute='get_total_with_tax')
    total_with_payment = fields.Float(string='Montant avec taxe', compute='get_total_payment_with')
    is_prive = fields.Boolean(default=True)
    journal_dest = fields.Many2one('account.journal', string='Journal Dest:')
    from_first = fields.Selection([('coc', 'Cocody')])
    enc = fields.Boolean()
    seq_id = fields.Char(string="ENC")
    com_num = fields.Char(string="COM_")
    com_id = fields.Boolean()

    @api.onchange('exist_facture_select')
    def onchange_exist_facture_select(self):
        self.num_facture = self.exist_facture_select.ref

    @api.onchange('somme')
    def onchange_dif_som_pay_inv(self):
        if self.facture:
            if self.somme > self.total_facture_with_tax:
                warning_mess = {
                    'title': _('Avertissement!'),
                    'message': _("le montant payé ne doit pas dépassr le montant de la facture !")
                }
                self.somme = 0
                return {'warning': warning_mess}

    @api.onchange('amount_facture')
    def onchange_amount_facture(self):
        if self.facture:
            if self.somme > self.total_facture_with_tax:
                warning_mess = {
                    'title': _('Avertissement!'),
                    'message': _("le montant payé ne doit pas dépasser le montant de la facture !")
                }
                self.somme = 0
                return {'warning': warning_mess}

    @api.depends('amount_facture', 'tax_id')
    def get_total_with_tax(self):
        for val in self:
            val.total_facture_with_tax = 0
            amount_t = self.env['account.tax'].sudo().search([('id', '=', val.tax_id.ids)])
            amount_tax = 0
            if amount_t:
                amount_tax = amount_t.amount
            if val.facture:
                val.total_facture_with_tax = abs(val.amount_facture) + (amount_tax * abs(val.amount_facture)) / 100
            else:
                val.total_facture_with_tax

    @api.depends('somme')
    def get_total_payment_with(self):
        for val in self:
            val.total_with_payment = abs(val.somme)

    @api.depends('somme')
    def get_total_somme(self):
        for som in self:
            som.total_somme = abs(som.somme)
            som.somme_lettre = num2words((abs(som.somme)), lang='fr') + ' ' + ' FCFA'

    @api.depends('somme')
    def get_somme_char(self):
        for som in self:
            som.somme_char = '{:,}'.format(abs(som.somme)).replace(',', ' ')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('account.yop')
        in_out = vals['check_in_out']
        if (in_out == 'sortie' or in_out == 'transfer') and not vals['etat']:
            if vals['somme'] != 0:
                vals['somme'] = - vals['somme']
        vals['update_by'] = self.env.uid
        vals['update'] = self.generate_update()
        vals['etat'] = True
        if 'visibility' in vals and vals['visibility'] == '0':
            vals['insible_somme'] = True
        vals.update({'journal_id': self._default_account_journal_id()})
        result = super(CaisseSecondaire, self).create(vals)
        return result

    def write(self, vals):
        for val in vals:
            self.message_post(body=str(val) + " ==>" + str(vals[val]))
        if self.check_in_out == 'sortie' and 'somme' in vals:
            if vals['somme'] > 0:
                vals['somme'] = - vals['somme']
        vals['update_by'] = self.env.uid
        vals['update'] = self.generate_update()
        result = super(CaisseSecondaire, self).write(vals)
        return result

    def unlink(self):
        for val in self:
            if val.status != 'brouillon':
                raise ValidationError(
                    _("Vous ne pouvez pas supprimer une opération validée ou en attente, veuillez mettre en brouillon d'abord !"))
        return super(CaisseSecondaire, self).unlink()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (Copy)") % self.name
        if 'status' not in default:
            default['status'] = 'brouillon'
        return super(CaisseSecondaire, self).copy(default=default)

    @api.depends('somme')
    def get_solde(self):
        amount = 0
        for agentis_dga in self:
            amount = int(amount + agentis_dga.somme)
            agentis_dga.solde = amount

    def put_suspense(self):
        self.status = 'attente'
        for val in self:
            val.message_post(body="status ==> En attente")
        return True

    def get_employee_in_partner(self, employee):
        if employee:
            partner = self.env['res.partner'].sudo().search([('user_associe_id', '=', employee.id)])
            if partner:
                return partner.id
            else:
                return employee.id

    def comptabilise_operation(self):
        for mov in self:
            print('début')
            if mov.status != 'comptabilise':
                mov.status = 'comptabilise'
                amount_t = self.env['account.tax'].sudo().search([('id', '=', mov.tax_id.ids)])
                amount_tax = amount_t.amount
                coeff = amount_t.exclude_amount  # exclude_amount génère une erreur

            if mov.check_in_out == 'transfer':
                caisse = self.env['account.bank.statement'].sudo().search(
                    [('date', '=', mov._default_time_utc()), ('journal_id', '=', mov.journal_id.id)])
                journal_dest = self.env['account.bank.statement'].sudo().search(
                    [('date', '=', mov._default_time_utc()), ('journal_id', '=', mov.journal_dest.id)])
                if caisse:
                    data = {
                        'journal_id': mov.journal_id.id,
                        'caisse_id': 'MAN' + str(mov.id),
                        'line_ids': [(0, 0, {
                            'date': mov.create_date,
                            'payment_ref': (mov.libele or ' '),
                            # 'partner_id': mov.partner_id.id,
                            'amount': mov.somme,
                            # 'caisse_id': 'MAN' + str(mov.id),

                        })]
                    }
                    caisse.write(data)
                else:
                    data = {
                        'name': 'Transfert vers Banque du ' + (str(mov.create_date)),
                        'date': mov.date,
                        'journal_id': mov.journal_id.id,
                        'caisse_id': 'MAN' + str(mov.id),
                        'line_ids': [(0, 0, {
                            'date': mov.create_date,
                            'payment_ref': (mov.libele or ' '),
                            # 'partner_id': mov.partner_id.id,
                            'amount': mov.somme,
                            # 'caisse_id': 'MAN' + str(mov.id),

                        })]
                    }
                    self.env['account.bank.statement'].create(data)
                if journal_dest:
                    data = {
                        'journal_id': mov.journal_dest.id,
                        'caisse_id': 'MAN' + str(mov.id),
                        'line_ids': [(0, 0, {
                            'date': mov.create_date,
                            'payment_ref': (mov.libele or ' '),
                            # 'partner_id': mov.partner_id.id,
                            'amount': abs(mov.somme),
                            # 'caisse_id': 'MAN' + str(mov.id),

                        })]
                    }
                    journal_dest.write(data)
                else:
                    data = {
                        'name': 'Transfert vers Banque du ' + (str(mov.create_date)),
                        'date': mov.date,
                        'journal_id': mov.journal_dest.id,
                        'caisse_id': 'MAN' + str(mov.id),
                        'line_ids': [(0, 0, {
                            'date': mov.create_date,
                            'payment_ref': (mov.libele or ' '),
                            # 'partner_id': mov.partner_id.id,
                            'amount': abs(mov.somme),
                            # 'caisse_id': 'MAN' + str(mov.id),

                        })]
                    }
                    self.env['account.bank.statement'].create(data)

            elif mov.beneficiaire_is == 'employee':
                all_val = {
                    'name': 'RELEVE du ' + (str(mov.create_date)),
                    'journal_id': mov._default_account_journal_id(),
                    'date': mov.create_date,
                    'line_ids': [(0, 0, {
                        'date': mov.create_date,
                        'payment_ref': (mov.libele or ' '),
                        # 'partner_id': mov.beneficiaire_employee.user_id.id,
                        'partner_id': self.env['res.users'].sudo().search(
                            [('id', '=', mov.beneficiaire_employee.user_id.id)]).partner_id.id,
                        'amount': mov.somme,
                        'caisse_id': mov.id
                    })]
                }
                emp = self.env['account.bank.statement'].sudo().search(
                    [('date', '=', mov.create_date), ('journal_id', '=', mov._default_account_journal_id())])
                if emp:
                    print("All val", all_val)
                    line = {
                        'date': mov.create_date,
                        'line_ids': [(0, 0, {
                            'date': mov.create_date,
                            'payment_ref': (mov.libele or ' '),
                            # 'partner_id': mov.beneficiaire_employee.user_id.id,
                            'partner_id': self.env['res.users'].sudo().search(
                                [('id', '=', mov.beneficiaire_employee.user_id.id)]).partner_id.id,
                            'amount': mov.somme,
                            'caisse_id': mov.id
                        })]
                    }
                    emp.write(line)
                else:
                    resut = self.env['account.bank.statement'].sudo().create(all_val)


            elif mov.beneficiaire_is == 'autre':
                autre_val = {
                    'name': 'RELEVE du ' + (str(mov.create_date)),
                    'journal_id': mov._default_account_journal_id(),
                    'date': mov.create_date,
                    'line_ids': [(0, 0, {
                        'date': mov.create_date,
                        'payment_ref': (mov.libele or ' '),
                        'partner_id': mov.beneficiaire_is_fournisseur.id,
                        'amount': mov.somme,
                        'caisse_id': mov.id
                    })]
                }
                emp = self.env['account.bank.statement'].sudo().search(
                    [('date', '=', mov.create_date), ('journal_id', '=', mov._default_account_journal_id())])
                if emp:
                    autre_line = {
                        'date': mov.create_date,
                        'line_ids': [(0, 0, {
                            'date': mov.create_date,
                            'payment_ref': (mov.libele or ' '),
                            'partner_id': mov.beneficiaire_is_fournisseur.id,
                            'amount': mov.somme,
                            'caisse_id': mov.id
                        })]
                    }
                    emp.write(autre_line)
                else:
                    resut = self.env['account.bank.statement'].sudo().create(autre_val)


            elif mov.facture == True:
                invoice_vals = {
                    'type_caisse': 'comptable',
                    'caisse_id': 'MOUV' + str(mov.id),
                    'associe_id': mov.id,
                    'borderau': mov.borderau,
                    'num_borderau': mov.num_borderau,
                    'ref': mov.name,
                    'payment_reference': mov.name,
                    'name': mov.num_facture,
                    'move_type': 'out_invoice',
                    'invoice_origin': mov.name,
                    'narration': '',
                    'somme_lettre': num2words((abs(mov.amount_facture) + (amount_tax * abs(mov.amount_facture)) / 100),
                                              lang='fr') + ' FCFA',
                    'partner_id': (
                            mov.beneficiaire_is_fournisseur or mov.beneficiaire_employee or mov.beneficiaire_is_client).id,
                    'commercial_partner_id': (
                            mov.beneficiaire_is_fournisseur or mov.beneficiaire_employee or mov.beneficiaire_is_client).id,
                    'currency_id': mov.currency_id.id,
                    'state': 'draft',
                    'invoice_date': mov.date_prevue,
                    'invoice_partner_display_name': (
                            mov.beneficiaire_is_fournisseur or mov.beneficiaire_employee or mov.beneficiaire_is_client).name,
                    'invoice_line_ids': [(0, 0, {
                        'name': mov.libele,
                        'price_unit': abs(mov.amount_facture),
                        'quantity': 1.0,
                        'product_id': self.get_product_id(),
                        'product_uom_id': mov.product_id.uom_id.id,
                        'analytic_account_id': mov.chantier_id.id or False,
                        'tax_ids': [(6, 0, mov.tax_id.ids)]
                    })],
                }
                # exclude_tax génère aussi une erreur
                if mov.tax_id.exclude_tax:
                    invoice_vals.update(
                        {'tax_exclude': (coeff * abs(mov.amount_facture)) / 100, 'tax_exclude_visible': True,
                         'somme_lettre': num2words((abs(mov.amount_facture)), lang='fr') + ' ' + ' FCFA'})
                else:
                    invoice_vals.update(
                        {'somme_lettre': num2words(
                            (abs(mov.amount_facture) + (amount_tax * abs(mov.amount_facture)) / 100),
                            lang='fr') + ' ' + ' FCFA'})

                if mov.beneficiaire_is == 'client':
                    invoice_vals.update({'move_type': 'out_invoice'})
                    resut = self.env['account.move'].sudo().create(invoice_vals)
                    print('resut =', resut)
                    resut.action_post()
                    mov.facture_id = resut.id

                elif mov.beneficiaire_is == 'fournisseur':
                    invoice_vals.update({'move_type': 'in_invoice'})
                    resut = self.env['account.move'].sudo().create(invoice_vals)
                    print('resut =', resut)
                    resut.action_post()
                    mov.facture_id = resut.id

                for payment in mov:
                    print('88888888888888888', payment.id)
                    paired_payment = {
                        'type_caisse': 'comptable',
                        'caisse_id': 'MOUV' + str(payment.id),
                        'associe_id': payment.id,
                        'journal_id': payment.journal_id.id,
                        'destination_journal_id': payment.journal_id.id,
                        'move_id': None,
                        'partner_id': (
                                mov.beneficiaire_is_fournisseur or mov.beneficiaire_employee or mov.beneficiaire_is_client).id,
                        'amount': abs(payment.somme),
                        'ref': payment.name,
                        'date': payment.create_date,
                    }

                    if self.beneficiaire_is == 'client':
                        print('.......................................ggg')
                        paired_payment.update({'payment_type': 'inbound'})
                        paired_payment.update({'partner_type': 'customer'})
                        resul = self.env['account.payment'].sudo().create(paired_payment)
                        resul.action_post()
                        self.payment_id = resul.id

                    elif self.beneficiaire_is == 'fournisseur':
                        print('---------------------------------------------gg')
                        paired_payment.update({'payment_type': 'outbound'})
                        paired_payment.update({'partner_type': 'supplier'})
                        resul = self.env['account.payment'].sudo().create(paired_payment)
                        resul.action_post()
                        self.payment_id = resul.id

            elif mov.facture == False:
                for payment in mov:
                    print('88888888888888888', payment.id)
                    paired_payment = {
                        'type_caisse': 'comptable',
                        'caisse_id': 'MOUV' + str(payment.id),
                        'associe_id': payment.id,
                        'journal_id': payment.journal_id.id,
                        'destination_journal_id': payment.journal_id.id,
                        'move_id': None,
                        'partner_id': (
                                mov.beneficiaire_is_fournisseur or mov.beneficiaire_employee or mov.beneficiaire_is_client).id,
                        'amount': abs(payment.somme) + (amount_tax * abs(payment.somme)) / 100,
                        'ref': payment.name,
                        'date': payment.create_date,
                    }

                    if self.beneficiaire_is == 'client':
                        print('.......................................ggg')
                        paired_payment.update({'payment_type': 'inbound'})
                        paired_payment.update({'partner_type': 'customer'})
                        resul = self.env['account.payment'].sudo().create(paired_payment)
                        resul.action_post()
                        self.payment_id = resul.id

                    elif self.beneficiaire_is == 'fournisseur':
                        print('---------------------------------------------gg')
                        paired_payment.update({'payment_type': 'outbound'})
                        paired_payment.update({'partner_type': 'supplier'})
                        resul = self.env['account.payment'].sudo().create(paired_payment)
                        resul.action_post()
                        self.payment_id = resul.id

                all_val = {
                    'name': 'MOUV BAN du ' + (str(mov.create_date)),
                    'journal_id': mov.journal_id.id,
                    'date': mov.create_date,
                    'company_id': mov.company_id.id,
                    'line_ids': [(0, 0, {
                        'date': mov.create_date,
                        'payment_ref': (mov.libele or mov.create_date),
                        'num_transaction': mov.name,
                        'partner_id': (
                                mov.beneficiaire_is_fournisseur or mov.beneficiaire_employee or mov.beneficiaire_is_client).id,
                        'amount': mov.somme,
                        'caisse_id': mov.id
                    })]
                }
                date_day = mov._default_time_utc()
                caisse_dga = self.env['account.bank.statement'].sudo().search(
                    [('date', '=', mov.create_date), ('journal_id', '=', mov.journal_id.id)])
                if caisse_dga:
                    if mov.beneficiaire_is == 'client' or mov.beneficiaire_is == 'fournisseur':
                        pass
                    else:
                        print('création caché du relévé')
                        if date_day.strftime('%Y-%m-%d') == str(mov.create_date):
                            line = {
                                'date': mov.create_date,
                                'line_ids': [(0, 0, {
                                    'date': mov.create_date,
                                    'payment_ref': mov.libele,
                                    'num_transaction': mov.name,
                                    'partner_id': (
                                            mov.beneficiaire_is_fournisseur or mov.beneficiaire_employee or mov.beneficiaire_is_client).id,
                                    'amount': mov.somme,
                                    'caisse_id': mov.id
                                })]
                            }
                            caisse_dga.write(line)
                            print('ici -------')
                        else:
                            self.env['account.bank.statement'].sudo().create(all_val)
                else:
                    self.env['account.bank.statement'].sudo().create(all_val)
                for val in mov:
                    val.message_post(body="statut ==> Validé")
            return True

    def put_draft(self):
        self.status = 'brouillon'
        facture = self.env['account.move'].sudo().search([('id', '=', self.facture_id)])
        if facture.state == 'posted':
            raise ValidationError(_('Vous ne pouvez pas remettre en brouillon une opération déjà comptabilisée'))
        else:
            facture.unlink()
            self.env['account.payment'].sudo().search([('id', '=', self.payment_id)]).unlink()
        for val in self:
            val.message_post(body="status ==> Brouillon")
        return True

    def generate_update(self):
        locale_time = datetime.now()
        return locale_time

    def open_journal_sold(self):
        action = {'type': 'ir.actions.act_window', 'name': 'Solde', 'view_mode': 'tree,form', 'view_type': 'form',
                  'res_model': 'account.bank.statement', 'view_id': False}
        domain = ([('name', '=', 'MOUV BAN du ' + (str(self.create_date))), ('journal_id', '=', self.journal_id.id)])
        action['domain'] = domain
        return action

    def open_payment(self):
        action = {'type': 'ir.actions.act_window', 'name': 'Paiements', 'view_mode': 'tree,form', 'view_type': 'form',
                  'res_model': 'account.payment', 'view_id': False}

        domain = ([('caisse_id', '=', 'MOUV' + str(self.id))])
        action['domain'] = domain
        return action

    def open_facture(self):
        action = {'type': 'ir.actions.act_window', 'name': 'Factures', 'view_mode': 'tree,form', 'view_type': 'form',
                  'res_model': 'account.move', 'view_id': False}
        if self.beneficiaire_is == 'fournisseur':
            domain = ([('caisse_id', '=', 'MOUV' + str(self.id)), ('move_type', '=', 'in_invoice')])
            action['domain'] = domain
        elif self.beneficiaire_is == 'client':
            domain = ([('caisse_id', '=', 'MOUV' + str(self.id)), ('move_type', '=', 'out_invoice')])
            action['domain'] = domain
        return action

    def put_validate(self):
        self.status = 'valide'
        for val in self:
            val.message_post(body="status ==> Validé")
        return True

    @api.model
    def retrieve_dashboard(self):
        """ This function returns the values to populate the custom dashboard in
            the office manager views.
        """
        self.check_access_rights('read')

        result = {
            'all_total_validate': 0,
            'all_total_draft': 0,
            'all_total_suspense': 0,
            'all_in': 0,
            'all_out': 0,
            'company_currency_symbol': self.env.company.currency_id.symbol
        }
        all_total_validate, all_total_draft, all_total_suspense, all_in, all_out = 0, 0, 0, 0, 0
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        office_manager = self.env['account.yop'].search([])
        for office in office_manager:
            if res_user.has_group('account_secii.secii_box_see_all'):
                if office.status == 'brouillon':
                    all_total_draft = all_total_draft + office.somme
                elif office.status == 'attente':
                    all_total_suspense = all_total_suspense + office.somme
                elif office.status == 'valide' or office.status == 'comptabilise':
                    all_total_validate = all_total_validate + office.somme
                    if office.check_in_out == 'entrer':
                        all_in += office.somme
                    if office.check_in_out == 'sortie' or office.check_in_out == 'transfer':
                        all_out += office.somme
            else:
                if not office.is_prive:
                    if office.status == 'brouillon':
                        all_total_draft = all_total_draft + office.somme
                    elif office.status == 'attente':
                        all_total_suspense = all_total_suspense + office.somme
                    elif office.status == 'valide' or office.status == 'comptabilise':
                        all_total_validate = all_total_validate + office.somme
                        if office.check_in_out == 'entrer':
                            all_in += office.somme
                        if office.check_in_out == 'sortie' or office.check_in_out == 'transfer':
                            all_out += office.somme

        result['all_total_validate'] = '{:,}'.format(all_total_validate).replace(',', ' ')
        result['all_total_suspense'] = '{:,}'.format(all_total_suspense).replace(',', ' ')
        result['all_total_draft'] = '{:,}'.format(all_total_draft + all_total_suspense).replace(',', ' ')
        result['all_in'] = '{:,}'.format(all_in).replace(',', ' ')
        result['all_out'] = '{:,}'.format(all_out).replace(',', ' ')
        return result
