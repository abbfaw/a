from datetime import datetime

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import pytz


class SeciiCommission(models.Model):
    _name = 'secii.commission'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Nouvelle Commission'
    _rec_name = 'commercial'
    _order = 'create_date desc'

    @api.model
    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    commercial = fields.Many2one('hr.employee', string="Commercial", required=True)
    status = fields.Selection([('impaye', 'IMPAYE'), ('paye', 'PAYE')], default='impaye')
    start_date = fields.Date(string='Date de début', required=True)
    end_date = fields.Date(string='Date de fin', required=True)
    taux = fields.Float('Taux de commission', compute='onchange_commercial_id')
    montant_encaisse = fields.Integer(string="Montant Encaissé", compute='daterange_calc')
    montant_commission = fields.Integer(string="Montant Commission", compute='calc_montant_commission',
                                        currency_field='currency_id')
    montant = fields.Integer(string="Montant")
    create_date = fields.Date(string='Date de création:', default=_default_time_utc, readonly=True)
    filter = fields.Char(compute="commission_filter")
    name = fields.Char(string="N° de bon")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=False, store=True,
                                  default=lambda self: self.env.company.currency_id)
    com_id = fields.Char(string="ID commission")
    is_paye = fields.Boolean(string="Déjà Payé", compute="check_commission_paye")
    caisse_id = fields.Char()
    # inst = fields.Boolean()

    @api.depends('start_date', 'end_date')
    def check_commission_paye(self):
        print('Check -----')
        verif = self.env['secii.commission'].sudo().search(
            [('start_date', '=', self.start_date), ('end_date', '=', self.end_date),
             ('taux', '=', self.commercial.taux_commission)]).mapped('commercial.id')
        print('verif =', verif)
        if verif:
            self.is_paye = True
        else:
            self.is_paye = False

    # récupération du taux quand le commercial change
    @api.onchange('commercial')
    def onchange_commercial_id(self):
        print('changement')
        for rec in self:
            rec.taux = rec.commercial.taux_commission

    # calcul du montant de la commission
    @api.onchange('montant_encaisse')
    def calc_montant_commission(self):
        print('calcul en cours')
        for rec in self:
            rec.montant_commission = (rec.montant_encaisse * rec.taux) / 100

    # recupération des montants en fonction de la période
    @api.depends('start_date', 'end_date')
    def daterange_calc(self):
        print('start_date')
        for dt in self:
            dt.montant_encaisse = 0
            if dt.end_date != 0:
                encaissement = self.env['secii.encaissement'].sudo().search(
                    [('date', '>=', dt.start_date), ('date', '<=', dt.end_date),
                     ('commercial', '=', dt.commercial.id)]).mapped('somme_paye')
                print('encaissement', encaissement)
                x = len(encaissement)
                print('x', x)
                for xz in encaissement:
                    dt.montant_encaisse += xz

    # def action_calcule(self):
    #     print('calculé')
    #     for verif in self:
    #         # if self.env['secii.commission'].search(
    #         #         [('start_date', '=', verif.start_date), ('end_date', '=', verif.end_date),
    #         #          ('taux', '=', verif.commercial.taux_commission)]).mapped('commercial.id'):
    #         #     raise ValidationError(
    #         #         _("la commission  a déjà été calculée. Veuillez sélectionner une nouvelle période"))
    #         # else:
    #         #     print('sortie')
    #             calcul_commission = {
    #                 'commercial': verif.commercial.id,
    #                 'start_date': verif.start_date,
    #                 'end_date': verif.end_date,
    #                 'montant': verif.montant_encaisse,
    #                 'montant_commission': verif.montant_commission,
    #                 'status': 'impaye',
    #                 'taux': verif.taux,
    #             }
    #             calc = self.env['secii.commission'].sudo().create(calcul_commission)

    # recherche du type de réglèment défini par défaut
    def _default_account_journal_id(self):
        journal = self.env['account.journal'].sudo().search([('code', '=', 'CAI'), ('company_id', '=', self.env.company.id)])
        return journal.id

    # empecher la suppression des données qui ont le statut payé
    def unlink(self):
        if self.status == 'paye':
            raise ValidationError(
                _("Vous ne pouvez pas supprimer une opération payée, veuillez mettre en impayé d'abord !"))
        return super(SeciiCommission, self).unlink()

    # Overwrite de la fonction create
    # @api.model
    # def create(self, vals):
    #     res = {}
    #     tau = self.env['hr.employee'].sudo().search([('id', '=', vals.get('commercial'))]).taux_commission
    #     crea = self.env['secii.commission'].sudo().search(
    #         [('start_date', '=', vals.get('start_date')), ('end_date', '=', vals.get('end_date')), ('taux', '=', tau)])
    #     if crea:
    #         res['warning'] = {'title': _('Warning'), 'message': _('Your Message Here.')}
    #     else:
    #         result = super(SeciiCommission, self).create(vals)
    #         return (res, result)
    #     # tau = self.env['hr.employee'].sudo().search([('id','=',vals.get('commercial'))]).taux_commission
    #     # print('tau', tau)
    #     # crea = self.env['secii.commission'].sudo().search([('start_date', '=', vals.get('start_date')), ('end_date', '=', vals.get('end_date')),('taux', '=', tau)])
    #     # print('-----crea-----', crea)
    #     # if crea:
    #     #     raise ValidationError(_("Impossible de créer un nouveau paiement de commission. Veuillez sélectionner une nouvelle période"))
    #     # result = super(SeciiCommission, self).create(vals)
    #     # return result

    # Overwrite de la fonction write
    # @api.model
    # def write(self, vals):
    #     tau = self.env['hr.employee'].sudo().search([('id', '=', vals.get('commercial'))]).taux_commission
    #     print('tau', tau)
    #     print('edt', vals.get('end_date'))
    #     print('edt_1', self.end_date)
    #     crea = self.env['secii.commission'].sudo().search(
    #         [('start_date', '=', vals.get('start_date')), ('end_date', '=', vals.get('end_date')), ('taux', '=', tau)])
    #     print('-----crea-----', crea)
    #     if crea:
    #         raise ValidationError(
    #             _("Impossible de créer un nouveau paiement de commission. Veuillez sélectionner une nouvelle période"))
    #     result = super(SeciiCommission, self).write(vals)
    #     return result

    # @api.onchange('inst')
    # def onchange_inst(self):
    #     print('Onchange ------', 'COM_' + str(self._origin.id))
    #     stat = self.env['account.secii'].sudo().search([('com_num', '=', 'COM_' + str(self._origin.id))])
    #     print('stat ------', stat)
    #     if stat:
    #         stat.write({"is_prive": self.inst})

    def open_caisse(self):
        action = {'type': 'ir.actions.act_window',
                  'name': 'Mouvement de Caisse',
                  'view_mode': 'tree,form',
                  'view_type': 'form',
                  'res_model': 'account.secii',
                  'view_id': False,
                  }

        domain = ([('com_num', '=', 'COM_' + str(self.id))])
        action['domain'] = domain
        return action

    # écrire dans le relevé les informations concernant les encaissements
    @api.depends('montant_commission')
    def action_paye(self):
        print('payé', self.montant_commission)
        self.status = 'paye'
        for val in self:
            val.message_post(body="status ==> Payé")
            mvt_caisse = {
                'name': val.num_de_sequence(),
                'type_caisse': 'comptable',
                'com_id': True,
                # 'is_prive': val.inst,
                'com_num': 'COM_' + str(val.id),
                'check_in_out': 'sortie',
                'libele': 'Commission du commercial ' + str(val.commercial.name),
                'etat': 'True',
                'date': val.create_date,
                'somme': -(val.montant_commission),
                'status': 'valide',
                'beneficiaire_employee': val.commercial.id
            }
            rez = self.env['account.secii'].sudo().create(mvt_caisse)
            val.caisse_id = 'COMMI' + str(rez.id)

        return True

    # génération de numéro de sequence
    def num_de_sequence(self):
        self.env['ir.sequence'].next_by_code('account.secii')

    # fonction permettant de passé le statut en impayé
    def action_impaye(self):
        print('impayé')
        self.status = 'impaye'
        print(self.status)
        for val in self:
            val.message_post(body="status ==> Impayé")
        return True

    # récupération du commercial connecté
    @api.depends('commercial')
    def _get_actual_user(self):
        context = self._context
        current_uid = context.get('uid')
        user = self.env['hr.employee'].sudo().search([
            ('user_id', '=', current_uid)])
        return user.id

    # action server filtrant la vue pour afficher la commission de l'employé
    def _commission_filter(self):
        print('ID commercial =', self._get_actual_user())
        return {
            "type": "ir.actions.act_window",
            "res_model": "secii.commission",
            "res_id": self.id,
            "views": [[self.env.ref('account_secii.encaissement_commisson_list').id, "tree"]],
            'view_mode': 'tree',
            "domain": [('status', '=', 'impaye'), ('commercial', '=', self._get_actual_user())],
            "name": "Ma commission",
            'target': 'new',
            'context': {'create': False},
        }

