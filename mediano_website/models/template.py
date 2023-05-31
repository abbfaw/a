from odoo import models, api, _, fields

class TemplateSms(models.Model):
    _name = 'template.sms'
    _description = 'SMS Templates'

    name = fields.Char(string='Template Name', required=False)
    sms_content = fields.Text(string='Sms Content', required=False)
