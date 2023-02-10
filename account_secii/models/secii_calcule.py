from datetime import datetime

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import pytz

class SeciiCommission(models.Model):
    _name = 'secii.calcule'

    @api.model
    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    commercial = fields.Many2one('hr.employee', string="Commercial")
    status = fields.Selection([('impaye', 'IMPAYE'), ('paye', 'PAYE')], default='impaye')
    start_date = fields.Date(string='Date de début')
    end_date = fields.Date(string='Date de fin')
    taux = fields.Float('Taux de commission', compute='onchange_commercial_id')
    montant_encaisse = fields.Integer(string="Montant Encaissé", compute='daterange_calc')
    montant_commission = fields.Integer(string="Montant Commission", compute='calc_montant_commission')
    montant = fields.Integer(string="Montant")
    create_date = fields.Date(string='Date de création:', default=_default_time_utc, readonly=True)