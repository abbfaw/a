from odoo import models, api, fields


class WhatsappMessage(models.TransientModel):
    _name = 'secii.whatsapp'
    _description = "Envoie du rapport par Whatsapp"

    partner = fields.Many2one('res.partner', string="Destinataire")
    mobile = fields.Char(related='partner.mobile', string="N° de Téléphone")
    message = fields.Text(string="Message")
    # attachment_ids = fields.Many2many(
    #     'ir.attachment', 'whatsapp_msg_ir_attachments_rel',
    #     'wizard_id', 'attachment_id', 'Pièce(s) Jointe(s)')
    # file = fields.Binary()

    @api.onchange('partner')
    def remplir_msg(self):
        print('Message Filled Sucessfully')
        rec = self.env['res.partner'].sudo().search([('id', '=', self.partner.id)])
        print('rec name =', rec.name)
        self.message = f"""Cher(e) {rec.name}, Sauf en cas d'erreur de notre part, il semble que le montant suivant reste impayé. S'il vous plaît, prenez les mesures appropriées afin d'effectuer ce paiement dans les 8 prochains jours. Si votre paiement a été effectué après l'envoi de ce courrier, veuillez ignorer ce message. N'hésitez pas à contacter notre service comptabilité. Meilleures salutations."""

    def send_message(self):
        return {
            'type': 'ir.actions.act_url',
            'url': "https://api.whatsapp.com/send?phone=+225" + self.partner.mobile + "&text=" + self.message,
            'target': 'new',
            'res_id': self.id,
        }

        # pdf = self.file
        # pdf_data = base64.b64decode(pdf)
        # with open("my_file.pdf", 'wb') as f:
        #     f.write(base64.b64decode(pdf))
        # # inputpath = r"account_secii/static/Bilan_client.pdf"
        #
        # # driver = webdriver.Chrome('C:/customs_addons/account_secii/static/chromedriver.exe')
        #
        # DRIVER_LOCATION = "/mnt/extra-addons/account_secii/static/chromedriver"
        # options = webdriver.ChromeOptions()
        # driver = webdriver.Chrome(executable_path=DRIVER_LOCATION)
        # driver.get("https://api.whatsapp.com/send?phone=" + self.mobile + "&text=" + self.message)
        #
        # sleep(90)
        # send_msg = driver.find_element(By.XPATH,
        #                                '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[2]/button/span')
        # send_msg.click()
        #
        # attachment_box = driver.find_element(By.XPATH, '//*[@id="main"]/footer//*[@data-icon="clip"]/..')
        # attachment_box.click()
        #
        # document = driver.find_element(By.XPATH, '//*[@id="main"]/footer//*[@data-icon="attach-document"]/../input')
        # document.send_keys('C:/odoo 15/server/my_file.pdf')
        #
        # sleep(3)
        #
        # send_button = driver.find_element(By.XPATH,
        #                                   '//*[@id="app"]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/div/div['
        #                                   '2]/div[2]/div/div/span')
        # send_button.click()
        #
        # sleep(1)
        #
        # menu = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[3]/header/div[2]/div/span/div[3]/div/span')
        # menu.click()
        #
        # sleep(1)
        #
        # logout = driver.find_element(By.XPATH,
        #                              '//*[@id="app"]/div/div/div[3]/header/div[2]/div/span/div[3]/span/div/ul/li['
        #                              '4]/div[1]')
        # logout.click()
        #
        # confirm = driver.find_element(By.XPATH,
        #                               '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div[3]/div/div[2]/div/div')
        # confirm.click()
        # sleep(1)
        # driver.close()
        # driver.quit()
        # return
