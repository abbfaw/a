# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CashInOut(models.Model):
    _name = 'cash.in.out'

    name = fields.Char(string='Wording')
    cash_type = fields.Char(string='Kind')
    amount = fields.Char(string='Amount')


class PaymentMethod(models.Model):
    _name = 'payment.method'

    name = fields.Char(string='Wording')
    amount = fields.Char(string='Amount')
