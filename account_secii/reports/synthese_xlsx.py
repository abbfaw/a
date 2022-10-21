from odoo import api, fields, models
from datetime import datetime
import pytz
from xlsxwriter import worksheet


class RapportClientXlsx(models.AbstractModel):
    _name = 'report.account_secii.report_secii_synthese_partner_xls'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Rapport de ventes et encaissements Excel'

    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     all_vals = {}
    #     tbl = []
    #     all_data = []
    #     amount = 0
    #     total_somme = 0
    #     total_vente = 0
    #     total_final = 0
    #     total_ant = 0
    #     print('tu es mt 01233.........885520', data)
    #     partner_id = data.get('client')
    #     start_date = data.get('start_date')
    #     end_date = data.get('end_date')
    #     scrap = self.env['res.partner'].sudo().search([('id', '=', partner_id)])
    #     name = scrap.name
    #     street = scrap.street
    #     date = datetime.now().strftime('%Y-%m-%d')
    #     payment = self.env['secii.encaissement']
    #     purchase = self.env['sale.order']
    #     print('partner_id', partner_id)
    #     all_orders = purchase.search([('partner_id', '=', partner_id), ('state', 'in', ('sale', 'done')),
    #                                   ('create_date', '>=', data.get('start_date')),
    #                                   ('create_date', '<=', data.get('end_date'))])
    #     print('all ------ orders ..', all_orders)
    #     all_paie = payment.search(
    #         [('partenaire', '=', partner_id), ('status', 'in', ('paye', 'comptabilise')),
    #          ('create_date', '>=', data.get('start_date')), ('create_date', '<=', data.get('end_date'))])
    #
    #     past_purchase = sum(purchase.search([('partner_id', '=', partner_id),
    #                                          ('state', 'in', ('sale', 'done')),
    #                                          ('create_date', '<', data.get('start_date'))]).mapped('amount_total'))
    #     print('rest g...........', past_purchase)
    #     past_payment = sum(payment.search(
    #         [('partenaire', '=', partner_id),
    #          ('status', 'in', ('paye', 'comptabilise')),
    #          ('date', '<', data.get('start_date'))]).mapped('somme_paye'))
    #     print('some   2222222222222222', past_payment)
    #
    #     all_date = all_orders.mapped('create_date') + all_paie.mapped("create_date")
    #     a = sorted(all_date)
    #     amount = (past_purchase - past_payment)
    #     for x in a:
    #         all_vals = {}
    #         var = purchase.sudo().search([("create_date", '=', x)])
    #         var2 = payment.sudo().search([("create_date", '=', x)])
    #         total_somme += var2.somme_paye
    #         total_vente += var.amount_total
    #         total_ant = past_purchase - past_payment
    #         total_final = total_vente + total_ant - total_somme
    #         print('var', var)
    #         print('var2', var2)
    #         if var:
    #             all_vals.update({
    #                 'name': var.name,
    #                 'partner_id': var.partner_id.name,
    #                 'user_id': var.user_id.name,
    #                 'amount_total': var.amount_total,
    #                 'debit': var.amount_total,
    #                 'credit': 0,
    #                 'somme_paye': 0,
    #                 'solde': amount + var.amount_total,
    #                 'designation': 'BL-' + str(var.name),
    #                 'create_date': var.create_date.strftime('%d-%m-%Y')
    #             })
    #             tbl.append(var.name)
    #             all_data.append(all_vals)
    #             amount += var.amount_total
    #         elif var2:
    #             all_vals.update({
    #                 'name': var2.num_seq,
    #                 'partner_id': var2.partenaire.name,
    #                 'user_id': var2.commercial.name,
    #                 'amount_total': var2.montant_total,
    #                 'debit': 0,
    #                 'credit': var2.somme_paye,
    #                 'somme_paye': var2.somme_paye,
    #                 'solde': amount - var2.somme_paye,
    #                 'designation': str(var2.num_seq),
    #                 'create_date': var2.date.strftime('%d-%m-%Y'),
    #             })
    #             tbl.append(var2.num_seq)
    #             all_data.append(all_vals)
    #             amount -= var2.somme_paye
    #     print('Tbl ===>', tbl)
    #     print('all_vals =>', all_vals)
    #     print('ADS =>', a)
    #     print('all pai', all_paie)
    #     print('all pai self ', self)
    #     print('all_data ', all_data)
    #     return {
    #         'docs': self.env['secii.synthese'].search([('id', '=', data.get('id'))]),
    #         'all_orders': all_orders,
    #         'all_paie': all_paie,
    #         'all_data': all_data,
    #         'amount': amount,
    #         'start_date': start_date,
    #         'end_date': end_date,
    #         'total_somme': total_somme,
    #         'total_vente': total_vente + total_ant,
    #         'total_final': total_final,
    #         'total_ant': total_ant,
    #         'name': name,
    #         'street': street,
    #         'date': date,
    #     }

    def generate_xlsx_report(self, workbook, data, rapport):
        print('Debut rappor Xlsx')
        all_vals = {}
        tbl = []
        all_data = []
        amount = 0
        total_somme = 0
        total_vente = 0
        total_final = 0
        total_ant = 0
        print('tu es mt 01233.........885520', data)
        partner_id = data.get('client')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        scrap = self.env['res.partner'].sudo().search([('id', '=', partner_id)])
        name = scrap.name
        street = scrap.street
        date = datetime.now().strftime('%Y-%m-%d')
        payment = self.env['secii.encaissement']
        purchase = self.env['sale.order']
        print('partner_id', partner_id)

        """"Recherche de toutes les ventes éffectuées entre les deux dates"""
        all_orders = purchase.search([('partner_id', '=', partner_id), ('state', 'in', ('sale', 'done')),
                                      ('date_effective', '>=', data.get('start_date')),
                                      ('date_effective', '<=',
                                       data.get('end_date'))])  # mettre create_date à la place de date_effective
        print('AO ->', all_orders)
        print('all ------ orders ..', all_orders)

        """Recherche de tous les encaissements éffectuéees entre les deux dates"""
        all_paie = payment.search(
            [('partenaire', '=', partner_id), ('status', 'in', ('paye', 'comptabilise')),
             ('date', '>=', data.get('start_date')), ('date', '<=', data.get('end_date'))])

        # past_purchase = sum(purchase.search([('partner_id', '=', partner_id),
        #                                      ('state', 'in', ('sale', 'done')),
        #                                      ('date_effective', '<', data.get('start_date'))]).mapped('amount_total'))

        """Recherche des ventes ultérieurs aux dates sélectionnées"""
        past_purchase = sum(purchase.search([('partner_id', '=', partner_id),
                                             ('state', 'in', ('sale', 'done')),
                                             ('date_effective', '<', data.get('start_date'))]).mapped('amount_total'))
        print('rest g...........', past_purchase)

        """Recherche des encaissements ultérieurs aux dates sélectionnées"""
        past_payment = sum(payment.search(
            [('partenaire', '=', partner_id),
             ('status', 'in', ('paye', 'comptabilise')),
             ('date', '<', data.get('start_date'))]).mapped('somme_paye'))
        print('some   2222222222222222', past_payment)

        """Concaténation des dates selon create_date et write_date pour un éventuel tri"""
        all_date = all_orders.mapped('date_effective') + all_paie.mapped("write_date")
        a = sorted(all_date)
        amount = (past_purchase - past_payment)

        """Boucle permettant la recherche des dates de façon ordonnée ainsi que l'attribution et le calcul de données"""
        for x in a:
            all_vals = {}
            var = purchase.sudo().search(
                [("date_effective", '=', x), ('partner_id', '=', partner_id)])  # erreur si remplacer par date_effective
            var2 = payment.sudo().search([("write_date", '=', x)])
            total_somme += var2.somme_paye
            for item in var:
                total_vente += item.amount_total
            total_ant = past_purchase - past_payment
            total_final = total_vente + total_ant - total_somme
            print('var', var)
            print('var2', var2)
            if var:
                all_vals.update({
                    'name': item.name,
                    'partner_id': item.partner_id.name,
                    'user_id': item.user_id.name,
                    'amount_total': item.amount_total,
                    'debit': item.amount_total,
                    'credit': 0,
                    'somme_paye': 0,
                    'solde': amount + item.amount_total,
                    'designation': 'BL-' + str(item.name),
                    'create_date': item.date_effective.strftime('%d-%m-%Y')
                })
                tbl.append(item.name)
                all_data.append(all_vals)
                amount += item.amount_total
            elif var2:
                all_vals.update({
                    'name': var2.num_seq,
                    'partner_id': var2.partenaire.name,
                    'user_id': var2.commercial.name,
                    'amount_total': var2.montant_total,
                    'debit': 0,
                    'credit': var2.somme_paye,
                    'somme_paye': var2.somme_paye,
                    'solde': amount - var2.somme_paye,
                    'designation': str(var2.num_seq),
                    'create_date': var2.write_date.strftime('%d-%m-%Y'),
                })
                tbl.append(var2.num_seq)
                all_data.append(all_vals)
                amount -= var2.somme_paye
        """-----------------------------------------------"""
        sheet = workbook.add_worksheet("Bilan du Client " + name)
        sheet.set_row(10, 20)
        sheet.set_column('C:E', 16)
        sheet.set_column('G:H', 16)
        sheet.set_column('B:B', 18)
        sheet.set_column('F:F', 18)
        """/------------ Mise en forme ------------/"""
        bold = workbook.add_format({'bold': True, 'valign': 'vcenter', 'align': 'center'})
        bo_c = workbook.add_format({'bold': True, 'left': 2, 'valign': 'vcenter', 'align': 'center'})
        merge_format = workbook.add_format({
            'bold': True,
            'border': 6,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#EC634D',
            'font_size': 14,
        })

        merge = workbook.add_format({'valign': 'vcenter', 'align': 'center', 'bold': True})

        center = workbook.add_format({'align': 'center',
                                      'border': 2,
                                      'left': 2,
                                      'valign': 'vcenter'})

        date = workbook.add_format()
        date.set_num_format({'dd/mm/yyyy'})

        currency_format = workbook.add_format({'num_format': '# ##0 ##0',
                                               'border': 2,
                                               'valign': 'vcenter',
                                               'align': 'center'})
        cur_format = workbook.add_format({'num_format': '# ##0 ##0',
                                          'valign': 'vcenter',
                                          'align': 'center',
                                          'bold': True})

        currency_format2 = workbook.add_format({'num_format': '# ##0 ##0',
                                                'fg_color': '#A29F9E',
                                                'valign': 'vcenter',
                                                'align': 'center',
                                                'bold': True})

        index_header = 2
        index_data = 12

        sheet.write('C2:D2', 'RELEVE DE COMPTE DU ' + str(start_date) + ' AU ' + str(end_date), merge)
        sheet.set_row(1, 20)
        # sheet.write(1, 2, str(start_date), date)
        # sheet.write(1, 3, 'au', bold)
        # sheet.write(1, 4, str(end_date), date)
        sheet.write('F4:G4', 'TOTAL SOLDE ANTERIEUR :', merge)
        sheet.set_row(5, 20)
        sheet.write(3, 7, total_ant, cur_format)
        sheet.set_row(3, 20)
        sheet.write(6, 1, name, bold)
        sheet.set_row(6, 20)
        sheet.write(8, 1, 'ADRESSE : ' + str(street), bold)
        sheet.set_row(8, 20)
        table_header = ["Date", "N° Commande", "Désignation", "Débit", "Crédit", "Montant"]
        for i in table_header:
            sheet.write(10, index_header, i, merge_format)
            index_header += 1
        sheet.write(11, 2, '   ', bo_c)
        sheet.write(11, 3, '   ', bo_c)
        sheet.write(11, 4, 'ANCIEN SOLDE', bo_c)
        sheet.set_row(11, 20)
        sheet.write(11, 5, total_ant, currency_format)
        sheet.write(11, 7, total_ant, currency_format)

        for elt in all_data:
            print('data =', elt)
            print(len(elt))
            # for x in elt:
            #     print('X =', x)
            sheet.write(index_data, 2, elt['create_date'], center)
            sheet.write(index_data, 3, elt['name'], center)
            sheet.write(index_data, 4, elt['designation'], center)
            sheet.write(index_data, 5, elt['debit'], currency_format)
            sheet.write(index_data, 6, elt['credit'], currency_format)
            sheet.write(index_data, 7, elt['solde'], currency_format)
            sheet.write(index_data + 1, 5, (total_vente + total_ant), currency_format)
            sheet.write(index_data + 1, 6, total_somme, currency_format)
            sheet.set_row(index_data, 20)
            sheet.set_row(index_data + 1, 20)
            print('Dernier index', index_data)
            index_data += 1
            sheet.write(index_data + 4, 4, 'SAUF ERREUR OU OMISSION, VOTRE SOLDE EST DE: ', bold)
            sheet.write(index_data + 4, 7, total_final, currency_format2)
            sheet.write(index_data + 3, 2, '   ')
            sheet.write(index_data + 3, 3, '   ')
            sheet.write(index_data + 3, 4, '   ')
            sheet.write(index_data + 3, 5, '   ')
            sheet.write(index_data + 3, 6, '   ')
            sheet.write(index_data + 3, 7, '   ')
            sheet.set_row(index_data + 4, 20)
