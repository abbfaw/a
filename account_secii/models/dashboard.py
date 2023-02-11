# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SeciiDashboard(models.Model):
    _name = 'secii.dashboard'

    t1 = fields.Char('Test1')
    t2 = fields.Char('Test2')
    t3 = fields.Char('Test3')
    t4 = fields.Char('Test4')
    t5 = fields.Char('Test5')