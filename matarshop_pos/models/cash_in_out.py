# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CashInOut(models.Model):
    _name = 'cash.in.out'

    name = fields.Char(string='Libele')
    cash_type = fields.Char(string='Type')
    amount = fields.Char(string='Montant')


class PaymentMethod(models.Model):
    _name = 'payment.method'

    name = fields.Char(string='Libele')
    amount = fields.Char(string='Montant')
