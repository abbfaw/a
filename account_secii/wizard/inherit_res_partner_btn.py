# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritAccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"