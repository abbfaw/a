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

    def generate_xlsx_report(self, workbook, data, rapport):
        print('Debut rappor Xlsx')
        all_vals = {}
        tbl = []
        all_data = []
        amount = 0
        total_somme = 0
        total_vente = 0
        total_retour = 0
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
        payment = self.env['secii.enc'].sudo()
        purchase = self.env['secii.vente'].sudo()
        retour = self.env['purchase.order'].sudo()
        print('partner_id', partner_id)
        all_orders = purchase.search(
            [('partner_id', '=', partner_id), ('date_order', '>=', start_date), ('date_order', '<=', end_date)])
        print('all ------ orders ..', all_orders)
        all_paie = payment.search(
            [('partenaire', '=', partner_id), ('status', '=', 'paye'),
             ('create_date', '>=', start_date), ('create_date', '<=', end_date)])

        all_return = retour.search(
            [('partner_id', '=', partner_id), ('state', '=', 'purchase'),
             ('write_date', '>=', start_date), ('write_date', '<=', end_date), ('retour', '=', True),
             ('is_prive', '=', True)])

        past_purchase = sum(purchase.search([('partner_id', '=', partner_id),
                                             ('date_order', '<', start_date)]).mapped('amount_total'))
        print('rest g...........', past_purchase)
        past_payment = sum(payment.search(
            [('partenaire', '=', partner_id),
             ('status', '=', 'paye'),
             ('date', '<', start_date)]).mapped('somme_paye'))
        print('some   2222222222222222', past_payment)
        past_retour = sum(retour.search([('partner_id', '=', partner_id),
                                         ('state', '=', 'purchase'),
                                         ('retour', '=', True),
                                         ('is_prive', '=', True),
                                         ('write_date', '<', start_date)]).mapped('amount_total'))
        print('reste retour...........', past_retour)

        all_date = all_orders.mapped('create_date') + all_paie.mapped("create_date") + all_return.mapped("write_date")
        a = sorted(all_date)
        print('A #1', a, 'Taille #1', len(all_orders), 'Taille #2', len(all_paie), 'Taille #3', len(all_return), )
        amount = (past_purchase - past_payment - past_retour)
        for x in a:
            print('A', len(a))
            all_vals = {}

            var = purchase.search(
                [("create_date", '=', x), ('partner_id', '=', partner_id)])
            # var = purchase.filtered(lambda l: not l.is_delivery)
            var2 = payment.search(
                [("create_date", '=', x), ('partenaire', '=', partner_id)])
            print('var2', var2)
            var3 = retour.search([("write_date", '=', x), ('partner_id', '=', partner_id), ('retour', '=', True),
                                  ('is_prive', '=', True)])
            print('Somme Payee', var2.mapped('somme_paye'))
            total_ant = past_purchase - past_payment
            print('var', var)

            for order in var:
                print('VAR', order.name)
                if order.name not in tbl:
                    all_vals.update({
                        'name': order.name,
                        'partner_id': order.partner_id.name,
                        'user_id': order.user_id.name,
                        'amount_total': order.amount_total,
                        'debit': order.amount_total,
                        'credit': 0,
                        'libele': ' ',
                        'somme_paye': 0,
                        'solde': amount + order.amount_total,
                        'designation': 'BL-' + str(order.name),
                        'numero_bon': order.numero_bon or ' ',
                        'create_date': order.date_order.strftime('%d-%m-%Y')
                    })
                    total_vente += order.amount_total
                    tbl.append(order.name)
                    all_data.append(all_vals)
                    print()
                    print('All Data #1', all_data)
                    print()
                    amount += order.amount_total
                    all_vals = {}
            for enc in var2:
                if enc.num_seq not in tbl:
                    print('ENCAISSEMENT', len(var2))
                    all_vals.update({
                        'name': enc.num_seq,
                        'partner_id': enc.partenaire.name,
                        'user_id': enc.commercial.name,
                        'amount_total': enc.montant_total,
                        'debit': 0,
                        'credit': enc.somme_paye,
                        'libele': enc.libele_op,
                        'somme_paye': enc.somme_paye,
                        'solde': amount - enc.somme_paye,
                        'designation': str(enc.num_seq),
                        'numero_bon': ' ',
                        'create_date': enc.create_date.strftime('%d-%m-%Y'),
                    })
                    total_somme += enc.somme_paye
                    tbl.append(enc.num_seq)
                    all_data.append(all_vals)
                    print()
                    print('All Data #2', all_data)
                    print()
                    amount -= enc.somme_paye
                    all_vals = {}
            for ret in var3:
                if ret.name not in tbl:
                    print('RETOUR', len(var3))
                    all_vals.update({
                        'name': ret.name,
                        'partner_id': ret.partner_id.name,
                        'user_id': ret.user_id.name,
                        'amount_total': ret.amount_total,
                        'debit': 0,
                        'credit': ret.amount_total,
                        'libele': ' ',
                        'somme_paye': 0,
                        'solde': amount - ret.amount_total,
                        'designation': 'RETOUR',
                        'numero_bon': ' ',
                        'create_date': ret.write_date.strftime('%d-%m-%Y'),
                    })
                    total_retour += ret.amount_total
                    tbl.append(ret.name)
                    all_data.append(all_vals)
                    print()
                    print('All Data #3', all_data)
                    print()
                    amount -= ret.amount_total
                    all_vals = {}
            total_final = total_vente + total_ant - total_somme - total_retour
        synthese = self.env['secii.synthese'].search([('id', '=', data.get('id'))])
        credit_client = 0
        if synthese.reste < 0:
            credit_client = synthese.reste
        """-----------------------------------------------"""
        sheet = workbook.add_worksheet("Bilan du Client " + name)
        sheet.set_row(10, 20)
        sheet.set_column('C:E', 16)
        sheet.set_column('G:J', 16)
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
        table_header = ["Date", "N° Commande", "Désignation", "Libellé", "N° de Bon", "Débit", "Crédit", "Montant"]
        for i in table_header:
            sheet.write(10, index_header, i, merge_format)
            index_header += 1
        sheet.write(11, 2, '   ', bo_c)
        sheet.write(11, 3, '   ', bo_c)
        sheet.write(11, 4, 'ANCIEN SOLDE', bo_c)
        sheet.write(11, 5, '   ', bo_c)
        sheet.write(11, 6, '   ', bo_c)
        sheet.write(11, 7, '   ', bo_c)
        sheet.write(11, 8, '   ', bo_c)
        sheet.write(11, 9, '   ', bo_c)
        sheet.set_row(11, 20)
        sheet.write(11, 7, total_ant, currency_format)
        sheet.write(11, 9, total_ant, currency_format)

        for elt in all_data:
            print('data =', elt)
            print(len(elt))
            # for x in elt:
            #     print('X =', x)
            sheet.write(index_data, 2, elt['create_date'], center)
            sheet.write(index_data, 3, elt['name'], center)
            sheet.write(index_data, 4, elt['designation'], center)
            sheet.write(index_data, 5, elt['libele'], center)
            sheet.write(index_data, 6, elt['numero_bon'], center)
            sheet.write(index_data, 7, elt['debit'], currency_format)
            sheet.write(index_data, 8, elt['credit'], currency_format)
            sheet.write(index_data, 9, elt['solde'], currency_format)
            sheet.write(index_data + 1, 7, (total_vente + total_ant), currency_format)
            sheet.write(index_data + 1, 8, (total_somme + total_retour), currency_format)
            sheet.set_row(index_data, 20)
            sheet.set_row(index_data + 1, 20)
            print('Dernier index', index_data)
            index_data += 1
            sheet.write(index_data + 4, 5, 'SAUF ERREUR OU OMISSION, VOTRE SOLDE EST DE: ', bold)
            sheet.write(index_data + 4, 8, total_final, currency_format2)
            sheet.write(index_data + 3, 3, '   ')
            sheet.write(index_data + 3, 4, '   ')
            sheet.write(index_data + 3, 5, '   ')
            sheet.write(index_data + 3, 6, '   ')
            sheet.write(index_data + 3, 7, '   ')
            sheet.write(index_data + 3, 8, '   ')
            sheet.set_row(index_data + 4, 20)
