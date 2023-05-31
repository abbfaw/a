# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sms_on_register = fields.Boolean(string="A l'inscription", config_parameter='mediano_website.sms_on_register')
    sms_on_confirm = fields.Boolean(string="A la validation de la commande",
                                    config_parameter='mediano_website.sms_on_confirm')

    email_activate = fields.Boolean(string="Se Connecter avec l'E-mail",
                                    config_parameter='mediano_website.email_activate')
    number_activate = fields.Boolean(string="Se Connecter avec le Numéro de Téléphone",
                                     config_parameter='mediano_website.number_activate')

    # recaptcha = fields.Boolean(string="Recaptcha V2")
    # recaptcha_cle_publique = fields.Char("Clé Publique", config_parameter='recaptcha_cle_publique')
    # recaptcha_cle_privee = fields.Char("Clé Secrète", config_parameter='recaptcha_cle_privee')
