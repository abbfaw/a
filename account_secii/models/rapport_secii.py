from odoo import fields, models, api
import io
import json
import xlsxwriter
from odoo.tools import date_utils
from datetime import datetime
import pytz


class RapportSecii(models.Model):
    _name = 'secii.rapport'
    _description = 'Rapport SECII'

    start_date = fields.Datetime(string='Date de debut')
    end_date = fields.Datetime(string='Date de fin')
    partner = fields.Many2one('res.partner', string='Client')

    def scrap_sale(self):
        print('Print Work -_-')
        data = {'id': self._context.get('active_id'), 'partner': self.partner.id, 'start_date': self.start_date.strftime('%d-%m-%Y'), 'end_date': self.end_date.strftime('%d-%m-%Y'), }
        return self.env.ref('account_secii.report_secii_synthese_partner').with_context(
            client_id=self.partner.id).report_action(self, data=data)

    def collecte_donnees(self):
        # print('Print Work -_-')
        data = {'id': self.id, 'partner': self.partner.id, 'start_date': self.start_date, 'end_date': self.end_date, }
        print('Data =', data)
        return self.env.ref('account_secii.report_secii_synthese_partner_xls').with_context(
            client_id=self.partner.id).report_action(self, data=data)
