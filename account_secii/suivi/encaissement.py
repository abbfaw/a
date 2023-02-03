from datetime import datetime
import pytz

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, RedirectWarning
from odoo.tools import float_round


def get_price_in_xof(currency_id, company_id, date):
    currency_name = currency_id.name
    if currency_name != 'XOF':
        rates = currency_id._get_rates(company_id, date)
        rate_value = 1
        if rates:
            for value in rates.values():
                rate_value = 1 / value
        return rate_value
    else:
        return 1


def get_xof_to_all_currency(currency):
    currency_name = currency.name
    if currency_name != 'XOF':
        cof = currency.rate_ids.company_rate

        return cof
    else:
        return 1


class PurchaseEncaissement(models.Model):
    _name = 'purchase.encaissement'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Nouvel Encaissement'
    _rec_name = 'num_seq'
    _order = 'create_date desc'

    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    # Avoir l'ID de l'utilisateur connecté
    def _get_actual_user(self):
        context = self._context
        current_uid = context.get('uid')
        user = self.env['hr.employee'].search([
            ('user_id', '=', current_uid)])
        return user.id

    def _default_company_currency(self):
        return self.env['res.currency'].search([('name', '=', 'XOF')]).id

    partner_id = fields.Many2one('res.partner', string="Fournisseur", required=True)
    somme_paye = fields.Float(string="Somme Payée", digit=2)
    date = fields.Date(string='Date ', default=_default_time_utc, tracking=True)
    note = fields.Text(string='Note', track_visibility='always')
    libele_op = fields.Text(string="Libellé d'opérations", default=' ')
    status = fields.Selection([('brouillon', 'BROUILLON'),
                               ('paye', 'PAYE')],
                              default='brouillon')
    num_seq = fields.Char(string="N° Enc")
    montant_total = fields.Float(string="Total Achats", group_operator=False)
    credit = fields.Float(string="Reste à payer")
    cumul = fields.Float(string="Cumul")
    somme_total_paye = fields.Float()
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id.id)
    company_currency_id = fields.Many2one('res.currency', string='Currency', default=_default_company_currency)
    payment_method = fields.Selection([('espece', 'Espèce'), ('bank', 'Banque'), ('box', 'Payer depuis la caisse')],
                                      string='Methode de paiement', default='espece')
    rel_client_id = fields.Many2one('purchase.synthese', string='Relevé du Client')
    amount_devise = fields.Char(string='Montant en Devise', compute='_compute_amount_total_signed')
    edit_rate = fields.Float(string="Taux de conversion", compute="_compute_rate", store=True)
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company)
    company_curreny_bool = fields.Boolean()
    purchase_direct_payment = fields.Char()
    amount_total_signed = fields.Float(string="Montant total en devise", store=True,
                                       currency_field='company_currency_id', compute='_compute_amount_total_signed')
    account_secii_id = fields.Many2one('account.secii', 'caisse')
    partner_type = fields.Selection([('customer', 'Client'), ('vendor', 'Fournisseur')])

    def _default_account_journal_id(self):
        journal = self.env['account.journal'].search([('code', '=', 'CAI'), ('company_id', '=', self.env.company.id)])
        return journal.id

    def update_exist_vendor_type(self):
        vendors = self.env['purchase.encaissement'].search([])
        for val in vendors:
            val.partner_type = 'vendor'

    @api.depends("somme_paye")
    def _compute_amount_total_signed(self):
        for val in self:
            val.amount_total_signed = val.somme_paye * get_price_in_xof(val.currency_id, val.company_id, val.date)
            val.amount_devise = (- val.somme_paye)

    @api.depends('currency_id')
    @api.onchange('currency_id', 'company_id')
    def _compute_rate(self):
        for move in self:
            if move.currency_id.name == move.company_id.currency_id.name:
                move.company_curreny_bool = True
                move.edit_rate = 1
            else:
                rates = move.currency_id._get_rates(move.company_id, move.date)
                rate_value = 1
                if rates:
                    for value in rates.values():
                        rate_value = 1 / value
                move.edit_rate = rate_value
                move.company_curreny_bool = False

    # fonction pour ouvrir la caisse et acceder à l'encaissement déjà crée
    def open_caisse(self):
        action = {'type': 'ir.actions.act_window',
                  'name': 'Mouvement de Caisse',
                  'view_mode': 'tree,form',
                  'view_type': 'form',
                  'res_model': 'account.secii',
                  'view_id': False,
                  }

        domain = ([('id', '=', self.account_secii_id.id)])
        action['domain'] = domain
        return action

    # fonction  permettant de payer l'encaissement
    # et  qui crée une ligne dans la caisse
    def put_validate(self):
        self.status = 'paye'

        for val in self:
            val.message_post(body="statut ==> Payé")
            if val.somme_paye < 0:
                raise ValidationError(_('Le montant à payer doit être supérieur à zéro'))
            if self.payment_method == 'box':
                box = self.env['account.secii'].search([('id', '=', self.account_secii_id.id)])
                self.payment_with_box(box)

            self.creation_rapport()
        return True

    def put_draft(self):
        line = self.env['account.secii'].search([('id', '=', self.account_secii_id.id)])
        if line:
            line.status = 'brouillon'
        for val in self:
            val.status = 'brouillon'
            val.message_post(body="statut ==> Brouillon")
        return True

    def creation_rapport(self):
        tracking_obj = self.env['tracking.partner'].sudo()
        for val in self:
            action = {
                'partner': val.partner_id.id,
                'reference': val.num_seq,
                'designation': 'Paiement',
                'payment_method': val.payment_method,
                'libele_op': val.libele_op,
                'date': self._default_time_utc(),
                'payment_ref': str(val.id) + 'PAI'

            }
            if val.partner_type == 'vendor':
                action.update({
                    'partner_type': 'vendor'
                })
            elif val.partner_type == 'customer':
                action.update({
                    'partner_type': 'customer'
                })
            exist = tracking_obj.search([('payment_ref', '=', str(val.id) + 'PAI')])
            if exist:
                if val.currency_id.name == 'XOF':
                    action.update({val.somme_paye})
                    if val.partner_type == 'customer':
                        action.update({'amount_currency': val.somme_paye})
                    exist.write(action)
            else:
                if val.currency_id.name == 'XOF':
                    action.update({'amount_currency': val.somme_paye})
                    if val.partner_type == 'customer':
                        action.update({val.somme_paye})
                    tracking_obj.create(action)

    @api.model
    def create(self, vals):
        vals['num_seq'] = self.env['ir.sequence'].next_by_code('purchase.encaissement')

        result = super(PurchaseEncaissement, self).create(vals)
        return result

    def unlink(self):
        for line in self:
            account_secii = self.env['account.secii'].search([('id', '=', self.account_secii_id.id)])
            tracking_obj = self.env['tracking.partner'].sudo().search([('payment_ref', '=', str(line.id) + 'PAI')])
            if tracking_obj:
                tracking_obj.unlink()
            if account_secii:
                account_secii.status = 'brouillon'
                account_secii.unlink()
        return super(PurchaseEncaissement, self).unlink()

    # cree une ligne dans la caisse principale
    def payment_with_box(self, box):
        data = {
            'libele': self.libele_op,
            'somme': float_round(self.somme_paye * get_price_in_xof(self.currency_id, self.company_id, self.date), 0),
            'date_prevue': self.date,
            'beneficiaire_is_fournisseur': self.partner_id.id,
            'etat': False,
            'note': self.note,
        }
        if self.partner_type == 'vendor':
            data.update({
                'beneficiaire_is': 'fournisseur',
                'check_in_out': 'sortie',
            })
        elif self.partner_type == 'customer':
            data.update({
                'beneficiaire_is': 'client',
                'check_in_out': 'entrer',
            })
        if box:
            box.sudo().write(data)
            box.put_validate()
        else:
            account_id = self.env['account.secii'].sudo().create(data)
            account_id.put_validate()
            self.account_secii_id = account_id
