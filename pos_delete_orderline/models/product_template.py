# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductPricelist(models.Model):
    _inherit = "product.template" 

    detailed_type = fields.Selection(default='product')
    
    available_in_pos =  fields.Boolean(default= True)