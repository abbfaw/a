from odoo import api, fields, models
from odoo.http import request
# from twilio.rest import Client


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    ville = fields.Selection([('abidjan', "Abidjan"), ('interieur', "Intérieur du pays")],
                             string="Lieu de livraison")

    commune_id = fields.Many2one('res.commune', store=True, index=True)
    ville_id = fields.Many2one('res.ville', store=True, index=True)

    sroom = fields.Char(string="Récupérer depuis le Showroom")
    plus_detail = fields.Char(string="Plus de détails")
    code = fields.Char()
    from_web = fields.Boolean(store=True)
    is_showroom = fields.Boolean(store=True)

    # def send_sms_twilio(self):
    #     """Fonction pour l'envoie de sms lors de l'inscription"""
    #     account_sid = 'AC0eacc095b5eec03c72edcc0f5fe748ec'
    #     auth_token = '2c019396c313b3e1179028804a056454'
    #     client = Client(account_sid, auth_token)
    #     number = ''.join(self.partner_id.phone.split(' '))
    #     print("Number", number)
    #     body = "Mr/Mme " + f"{self.partner_id.name}" + " Votre compte a bien été crée. Merci de nous faire confiance! "
    #     from_ = "+15108226061"
    #     to = "+2250757110861"
    #     try:
    #         message = client.messages.create(body=body, from_=from_, to=to)
    #         print(message.body, f"{self.partner_id.name}")
    #     except:
    #         print("Vérifiez votre numéro de telephone")

class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    phone_num = fields.Char(string='N° de Téléphone', related='partner_id.phone')
