from datetime import datetime

import pytz

from odoo import fields, models, api, _
from num2words import num2words

from odoo.exceptions import ValidationError


class InheritAccountMove(models.Model):
    _inherit = 'account.move'

    caisse_id = fields.Char(string='ID Caisse')
    type_caisse = fields.Selection([('dga', 'DGA'), ('manager', 'Office manager'), ('comptable', 'Comptable')],
                                   'Type de caisse')
    somme_lettre = fields.Text(string='Somme Letter')
    tax_exclude = fields.Char(string='TVA non facturée:')
    tax_exclude_visible = fields.Boolean(string='visibility')
    associe_id = fields.Many2one('account.secii', string='Mouvement lié')
    # manager_id = fields.Many2one('account.secii', string='Mouvement lié')
    borderau = fields.Boolean(string='Borderau de livraison')
    num_borderau = fields.Char(string='N° Borderau')
    associe_yop_id = fields.Many2one('account.yop', string='Mouvement yop lié')
    objet_facture = fields.Char(string=' Object de la facture')
    comp_id = fields.Many2one('res.company', string='Société:', required=False, default=lambda self: self.env.company)
    # bank_reception = fields.Many2one('agentis.bank', string='Banque Partenaire:')
    # fideca = fields.Boolean(string='FIDECA')
    maroc = fields.Boolean(string='Maroc')
    remise_global = fields.Boolean(string='Remise globale')
    amount_remise = fields.Float(string='Montant remise')
    with_discount = fields.Boolean(string='Avec remise')
    all_name = fields.Char(string='All project name', compute='get_all_project_name')

    @api.model
    def _get_tax_totals(self, partner, tax_lines_data, amount_total, amount_untaxed, currency):
        """if self.remise_global:
            total = self.compute_amount_discount(self.amount_remise, self.invoice_line_ids)
            print('total..............', total)
            for line in self.invoice_line_ids:
                print('subppppppppppp', line.price_subtotal)
                line.write({'discount': 20})"""
        res = super(InheritAccountMove, self)._get_tax_totals(partner, tax_lines_data, amount_total, amount_untaxed,
                                                              currency)
        if tax_lines_data:
            tax = tax_lines_data[0]['tax']
            tax_use = self.env['account.tax'].search([('id', '=', tax._origin.id)])
            amount_tax = tax_use.exclude_amount
            if tax_use.exclude_tax:
                self.tax_exclude_visible = True
                self.tax_exclude = (amount_tax * abs(amount_untaxed)) / 100
        self.somme_lettre = num2words(res['amount_total'], lang='fr') + ' ' + ' FCFA'
        # la fonction qui permet de fait les lignes: _recompute_dynamic_lines

        return res

    # fonction pour recuperer les projets
    def get_all_project_name(self):
        for line in self:
            data = []
            line.all_name = ''
            for ln in line.invoice_line_ids:
                if ln.analytic_account_id.id not in data:
                    line.all_name += '- ' + ln.analytic_account_id.name
                    data.append(ln.analytic_account_id.id)

    # fonction pour ouvrir les factures
    @api.onchange("invoice_line_ids", "amount_remise", "remise_global")
    def _onchange_invoice_line_ids(self):
        others_lines = self.line_ids.filtered(
            lambda line: line.exclude_from_invoice_tab
        )
        if others_lines:
            others_lines[0].recompute_tax_line = True
        if self.invoice_line_ids and self.remise_global and (
                self.amount_remise == 0.0 or not self.amount_remise):
            for line in self.invoice_line_ids:
                if self.remise_global and self.amount_remise == 0.0:
                    line.line_discount_amount = 0
                    line.discount = 0
                line._onchange_price_subtotal()
                line.recompute_tax_line = True
        if self.invoice_line_ids and self.amount_remise:
            for line in self.invoice_line_ids:
                # if self.invoice_discount_type == False:
                if self.remise_global and self.amount_remise == 0.0:
                    line.line_discount_amount = 0
                    line.discount = 0
                line.discount = 0
                total_price = [val.price_unit * val.quantity for val in self.invoice_line_ids]
                total_price = sum(total_price)
                if total_price != 0:
                    line.line_discount_amount = (
                            ((line.price_unit * line.quantity) / total_price) * (self.amount_remise))
                    line.line_discount_amount = round(line.line_discount_amount, 4)
                if line.price_unit * line.quantity != 0:
                    line.discount = (100 * line.line_discount_amount) / (line.price_unit * line.quantity)
                line._onchange_price_subtotal()
                line.recompute_tax_line = True
        res = super()._onchange_invoice_line_ids()
        self._onchange_recompute_dynamic_lines()
        return res

    # fonction pour ouvrir les paiements associés
    def open_payment_associate(self):
        action = {'type': 'ir.actions.act_window', 'name': 'Paiements', 'view_mode': 'tree,form', 'view_type': 'form',
                  'res_model': 'account.payment', 'view_id': False}

        domain = ([('caisse_id', '=', self.caisse_id)])
        action['domain'] = domain
        return action

    @api.model
    def create(self, vals_list):
        moves = super(InheritAccountMove, self).create(vals_list)
        for move in moves:
            move.with_context(check_move_validity=False)._onchange_invoice_line_ids()
        # self.on_add_discount(moves)
        return moves

    # def button_draft(self):
    #     for line in self:
    #         manager_id = line.manager_id
    #         manager = self.env['office.manager'].search([('id', '=', manager_id.id)])
    #         if manager:
    #             raise ValidationError(
    #                 _("Vous ne pouvez pas remettre en brouillon un paiement venant de la caisse secondaire !"
    #                   " \n veuillez modifier directement au niveau de la caisse secondaire"))
    #     return super(InheritAccountMove, self).button_draft()

    # fonction pour les promotions
    def on_add_discount(self, moves):
        for line in moves:
            for ln in line.invoice_line_ids:
                if ln.discount != 0.0:
                    ln.with_discount = True

    """@api.onchange('line_ids', 'invoice_payment_term_id', 'invoice_date_due', 'invoice_cash_rounding_id', 'invoice_vendor_bill_id')
    def _onchange_recompute_dynamic_lines(self):
        res = super(InheritAccountMove, self)._onchange_recompute_dynamic_lines()
        print('fffffffffffffffffffffffffffff', self.line_ids)
        for line in self.line_ids:
            print('tax id ******', line)
            print('self ----', self)
            if line.tax_line_id.exclude_tax:
                tax_use = line.tax_line_id.amount
                print('dododo ----', tax_use)
                #line.tax_line_id.action_archive()
                # self.tax_exclude = (tax_use * abs(amount_untaxed)) / 100"""


class InheritAccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    caisse_id = fields.Char(string='ID Caisse')
    type_caisse = fields.Selection([('manager', 'Caisse'), ('comptable', 'Encaissement')])
    somme_lettre = fields.Text(string='Somme Letter')
    associe_id = fields.Many2one('account.secii', string='Mouvement lié')
    associe_yop_id = fields.Many2one('account.yop', string='Mouvement yop lié')
    # bank_reception = fields.Many2one('agentis.bank', string='Banque Réceptrice')
    methode_payment = fields.Selection(
        [('virement', 'Virement'), ('versement', 'Versement'), ('misedispo', 'Mise à Disposition'),
         ('chequebarre', 'Chèque Barré'), ('chequenonbarre', 'Chèque Non Barré'), ('espece', 'Espèce'),
         ('prele', 'Prélèvement'), ('traite', 'Traite'), ('finance', 'Financement')],
        "Méthode de paiément", default='virement')
    type_operation = fields.Selection([('local', 'Local'), ('inter', 'International')], "Type d'operation",
                                      default='local')
    date_escompte = fields.Date(string="Date d'escompte")
    origin_fond = fields.Many2many('origin.fond', store=True, string='origine des fonds', readonly=False)
    num_transaction = fields.Char(string='N° transaction')
    libele = fields.Text(string='Libelé', default='aucun')
    chantier_id = fields.Many2one('account.analytic.account', string="Projet")
    from_popup = fields.Boolean(string='Popup', default=False)
    select_operation = fields.Selection([('espece', 'Espèce'), ('banque', 'Banque')], string='Moyen de paiement',
                                        default='banque')
    # fideca = fields.Boolean(string='FIDECA')
    maroc = fields.Boolean(string='MAROC')
    nature = fields.Char(string="Nature de l'operation")

    @api.model
    def create(self, vals_list):
        vals_list['somme_lettre'] = num2words(vals_list['amount'], lang='fr')
        res = super(InheritAccountPayment, self).create(vals_list)
        return res

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type == 'tree':
    #         self.update_num_check()
    #     return res

    # fonction pour les num de transactions
    def update_num_check(self):
        all_payment = self.env['account.payment'].search([])
        for line in all_payment:
            if not line.ref:
                line.ref = line.num_transaction

    # fonction pour ouvrir les factures associées
    def open_facture_associate(self):
        action = {'type': 'ir.actions.act_window', 'name': 'Factures', 'view_mode': 'tree,form', 'view_type': 'form',
                  'res_model': 'account.move', 'view_id': False}
        if self.partner_type == 'customer':
            domain = ([('caisse_id', '=', self.caisse_id), ('move_type', '=', 'out_invoice')])
        elif self.partner_type == 'supplier':
            domain = ([('caisse_id', '=', self.caisse_id), ('move_type', '=', 'in_invoice')])
        action['domain'] = domain
        return action

    # def action_draft(self):
    #     res = super(InheritAccountPayment, self).action_draft()
    #     for line in self:
    #         manager_id = line.manager_id
    #         manager = self.env['office.manager'].search([('id', '=', manager_id.id)])
    #         if manager:
    #             raise ValidationError(
    #                 _("Vous ne pouvez pas remettre en brouillon un paiement venant de la caisse secondaire !"
    #                   " \n veuillez modifier directement au niveau de la caisse secondaire"))
    #     return res

    # fonction pour créer les lignes dans les relevés
    def action_post(self):
        res = super(InheritAccountPayment, self).action_post()
        for pay in self:
            if pay.from_popup:
                if 'active_id' in self._context:
                    move = self.env['account.move'].search([('id', '=', self._context['active_id'])])
                    for line in move.invoice_line_ids:
                        pay.chantier_id = line.analytic_account_id
            move_line = self.env['account.bank.statement.line'].search([('caisse_id', '=', 'PAI' + str(pay.id))])
            if move_line:
                line = {
                    'date': pay.date,
                    'caisse_id': 'PAI' + str(pay.id),
                    'payment_ref': pay.libele,
                    'num_transaction': pay.num_transaction,
                    'partner_id': pay.partner_id.id,
                    'chantier_id': pay.chantier_id.id,
                    'ref': pay.ref,
                    'nature': pay.nature,
                    'methode_payment': pay.methode_payment,
                    'type_operation': pay.type_operation,
                }
                if pay.partner_type == 'supplier':
                    line.update({'amount': - abs(pay.amount)})
                move_line.write(line)
            elif self._context.get('active_model') == 'account.payment':
                print('je crée un relevé')
                all_val = {
                    'name': 'RELEVE DU ' + (str(pay.date)),
                    'journal_id': pay.journal_id.id,
                    'date': pay.date,
                    'date_prevue': datetime.now(),
                    'company_id': pay.company_id.id,
                    'line_ids': [(0, 0, {
                        'date': pay.date,
                        'caisse_id': 'PAI' + str(pay.id),
                        'payment_ref': pay.libele,
                        'num_transaction': pay.num_transaction,
                        'partner_id': pay.partner_id.id,
                        'amount': pay.amount,
                        'chantier_id': pay.chantier_id.id,
                        'ref': pay.ref,
                        'nature': pay.nature,
                        'methode_payment': pay.methode_payment,
                        'type_operation': pay.type_operation,
                    })]
                }
                if pay.partner_type == 'supplier':
                    all_val.update({
                        'line_ids': [(0, 0, {
                            'date': pay.date,
                            'caisse_id': 'PAI' + str(pay.id),
                            'payment_ref': pay.libele,
                            'num_transaction': pay.num_transaction,
                            'partner_id': pay.partner_id.id,
                            'amount': - abs(pay.amount),
                            'chantier_id': pay.chantier_id.id,
                            'ref': pay.ref,
                            'nature': pay.nature,
                            'methode_payment': pay.methode_payment,
                            'type_operation': pay.type_operation,
                        })]
                    })
                date_day = pay._default_time_utc()
                caisse_dga = pay.env['account.bank.statement'].sudo().search(
                    [('date', '=', pay.date), ('journal_id', '=', pay.journal_id.id)])
                if caisse_dga:
                    if date_day.strftime('%Y-%m-%d') == str(pay.date):
                        line = {
                            'date': pay.date,
                            'line_ids': [(0, 0, {
                                'date': pay.date,
                                'caisse_id': 'PAI' + str(pay.id),
                                'payment_ref': pay.libele,
                                'num_transaction': pay.num_transaction,
                                'partner_id': pay.partner_id.id,
                                'amount': pay.amount,
                                'chantier_id': pay.chantier_id.id,
                                'ref': pay.ref,
                                'nature': pay.nature,
                                'methode_payment': pay.methode_payment,
                                'type_operation': pay.type_operation,
                            })]
                        }
                        if pay.partner_type == 'supplier':
                            line.update({
                                'line_ids': [(0, 0, {
                                    'date': pay.date,
                                    'caisse_id': 'PAI' + str(pay.id),
                                    'payment_ref': pay.libele,
                                    'num_transaction': pay.num_transaction,
                                    'partner_id': pay.partner_id.id,
                                    'amount': - abs(pay.amount),
                                    'chantier_id': pay.chantier_id.id,
                                    'ref': pay.ref,
                                    'nature': pay.nature,
                                    'methode_payment': pay.methode_payment,
                                    'type_operation': pay.type_operation,
                                })]
                            })
                        caisse_dga.write(line)
                    else:
                        self.env['account.bank.statement'].sudo().create(all_val)
                else:
                    self.env['account.bank.statement'].sudo().create(all_val)

        return res


class InheritAccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'
    caisse_id = fields.Char('caisse id')
    num_transaction = fields.Char(string='N° transaction')
    # bank_reception = fields.Many2one('agentis.bank', string='Banque Emettrice')
    methode_payment = fields.Selection(
        [('virement', 'Virement'), ('versement', 'Versement'), ('misedispo', 'Mise à Disposition'),
         ('chequebarre', 'Chèque Barré'), ('chequenonbarre', 'Chèque Non Barré'), ('espece', 'Espèce'),
         ('prele', 'Prélèvement'), ('traite', 'Traite'), ('finance', 'Financement')],
        "Méthode de paiément", default='espece')
    type_operation = fields.Selection([('local', 'Local'), ('inter', 'International')], "Type d'operation")
    date_escompte = fields.Date(string="Date d'escompte")
    origin_fond = fields.Many2many('origin.fond', store=True, string='origine des fonds', readonly=False)
    chantier_id = fields.Many2one('account.analytic.account', string="Projet")
    nature = fields.Char(string="Nature de l'operation")
    company_id = fields.Many2one('res.company', string='Société:', default=lambda self: self.env.company)

    # def unlink(self):
    #     for line in self:
    #         name = line.num_transaction
    #         manager = self.env['office.manager'].search([('name', '=', name)])
    #         if manager:
    #             raise ValidationError(
    #                 _("Vous ne pouvez pas remettre en brouillon un paiement venant de la caisse secondaire !"
    #                   " \n veuillez modifier directement au niveau de la caisse secondaire"))
    #     return super(InheritAccountBankStatementLine, self).unlink()


class InheritAccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'
    caisse_id = fields.Char('caisse id')
    date_prevue = fields.Date(string="Date validation")


class InheritAccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    num_contrat = fields.Many2one('agentis.contrat', string='Numéro du contrat')
    identify_uni = fields.Char(string='Identifiant Unique')
    line_discount_amount = fields.Float(string="Disc.(amt)", digits="Discount", default=0.00)
    balance_cumule = fields.Monetary(string='Solde')
    with_discount = fields.Boolean(string="Avec remise")

    # fonction pour obtenir le num de contrat
    @api.onchange('analytic_account_id')
    def get_contrat_num(self):
        for val in self:
            print('VAL', val.analytic_account_id)
            val.identify_uni = val.analytic_account_id.identify_uni

    # fonction pour calculer la balance cumulée
    @api.depends_context('order_cumulated_balance', 'domain_cumulated_balance')
    def _compute_cumulated_balance(self):
        res = super(InheritAccountMoveLine, self)._compute_cumulated_balance()
        if not self.env.context.get('order_cumulated_balance'):
            # We do not come from search_read, so we are not in a list view, so it doesn't make any sense to compute the cumulated balance
            self.cumulated_balance = 0
            return

        # get the where clause
        query = self._where_calc(list(self.env.context.get('domain_cumulated_balance') or []))
        order_string = ", ".join(
            self._generate_order_by_inner(self._table, self.env.context.get('order_cumulated_balance'), query,
                                          reverse_direction=True))
        from_clause, where_clause, where_clause_params = query.get_sql()
        sql = """
                SELECT account_move_line.id, SUM(account_move_line.balance) OVER (
                    ORDER BY %(order_by)s
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                )
                FROM %(from)s
                WHERE %(where)s
            """ % {'from': from_clause, 'where': where_clause or 'TRUE', 'order_by': order_string}
        self.env.cr.execute(sql, where_clause_params)
        result = {r[0]: r[1] for r in self.env.cr.fetchall()}
        for record in self:
            record.cumulated_balance = result[record.id]
            record.balance_cumule = result[record.id]

        return res

    # fonction pour mettre a jour le compte analytique
    def update_analytic_account(self):
        lines = self.env['account.move.line'].search([])
        for line in lines:
            payment = self.env['account.payment'].search([('date', '=', line.date), ('ref', '=', line.ref)])
            if payment:
                for pay in payment:
                    if len(line.analytic_account_id) == 0:
                        line.analytic_account_id = pay.chantier_id

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type == 'tree':
    #         self.update_analytic_account()
    #     return res


class InheritAccountAnalytiqueAccount(models.Model):
    _inherit = 'account.analytic.account'

    identify_uni = fields.Char(string='Identifiant Unique')
