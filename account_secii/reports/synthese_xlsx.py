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
        print('tu es mt 07571.........10861', data)
        partner_id = data.get('partner')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        scrap = self.env['res.partner'].sudo().search([('id', '=', partner_id)])
        name = scrap.name
        street = scrap.street
        Date = datetime.now().strftime('%Y-%m-%d')
        tracking = self.env['tracking.partner'].sudo()
        print('partner_id', partner_id)

        """Recherche dans la table Tracking partner"""
        new_search = self.env['tracking.partner'].sudo().search(
            [('partner', '=', partner_id), ('date', '>=', start_date), ('date', '<=', end_date)], order='date asc')

        """ Recherche de tous ce qui est passés """
        past_amount_currency = sum(tracking.search(
            [('partner', '=', partner_id), ('date', '<', start_date), ('partner_type', '=', 'customer')]).mapped(
            'amount_currency'))
        print('PAST AMount', past_amount_currency)

        total_amount_currency = sum(tracking.search(
            [('partner', '=', partner_id), ('date', '>=', start_date), ('date', '<=', end_date),
             ('partner_type', '=', 'customer')]).mapped(
            'amount_currency'))
        print('Total AMount', total_amount_currency)

        amount = past_amount_currency
        # print('Tracking ------ orders ..', tracking_orders)
        for elt in new_search:
            """Pièces comptables +"""
            if elt.designation == 'Pièces comptables':
                all_vals.update({
                    'name': elt.reference,
                    'partner_id': elt.partner.name,
                    'amount_total': elt.amount_currency,
                    'debit': elt.amount_currency,
                    'credit': 0,
                    'libele': elt.libele_op or ' ',
                    'somme_paye': 0,
                    'solde': amount + elt.amount_currency,
                    'designation': 'SOLDE INITIAL',
                    'libele_op': ' ',
                    'create_date': elt.date.strftime('%d-%m-%Y'),
                })
                tbl.append(elt.purchase_ref)
                all_data.append(all_vals)
                print()
                print('All Data #0', all_data)
                print()
                amount += elt.amount_currency
                all_vals = {}

            """Ventes +"""
            if elt.designation == 'Vente':
                all_vals.update({
                    'name': elt.reference,
                    'partner_id': elt.partner.name,
                    # 'user_id': elt.user_id.name,
                    'amount_total': elt.amount_currency,
                    'debit': elt.amount_currency,
                    'credit': 0,
                    'libele': ' ',
                    'somme_paye': 0,
                    'solde': amount + elt.amount_currency,
                    # 'designation': 'BL-' + str(elt.reference),
                    'designation': 'VENTE',
                    'libele_op': elt.libele_op or ' ',
                    'create_date': elt.date.strftime('%d-%m-%Y'),
                })
                tbl.append(elt.purchase_ref)
                all_data.append(all_vals)
                print()
                print('All Data #1', all_data)
                print()
                amount += elt.amount_currency
                all_vals = {}

            """Achats +"""
            if elt.designation == 'Retour Achat':
                all_vals.update({
                    'name': elt.reference,
                    'partner_id': elt.partner.name,
                    # 'user_id': tracking_orders.user_id.name,
                    'amount_total': elt.amount_currency,
                    'debit': 0,
                    'credit': elt.amount_currency,
                    'libele': elt.libele_op or ' ',
                    'somme_paye': 0,
                    'solde': amount + elt.amount_currency,
                    # 'designation': 'BL-' + str(elt.reference),
                    'designation': "RETOUR D'ACHAT",
                    'libele_op': ' ',
                    'create_date': elt.date.strftime('%d-%m-%Y'),
                })
                tbl.append(elt.purchase_ref)
                all_data.append(all_vals)
                print()
                print('All Data #2', all_data)
                print()
                amount += elt.amount_currency
                all_vals = {}

            """Factures +"""
            if elt.designation == 'Facture Vente':
                all_vals.update({
                    'name': elt.reference,
                    'partner_id': elt.partner.name,
                    # 'user_id': tracking_orders.user_id.name,
                    'amount_total': elt.amount_currency,
                    'debit': elt.amount_currency,
                    'credit': 0,
                    'libele': elt.libele_op or ' ',
                    'somme_paye': 0,
                    'solde': amount + elt.amount_currency,
                    # 'designation': str(elt.reference),
                    'designation': 'FACTURE',
                    'libele_op': ' ',
                    'create_date': elt.date.strftime('%d-%m-%Y'),
                })
                tbl.append(elt.reference)
                all_data.append(all_vals)
                print()
                print('All Data #3', all_data)
                print()
                amount += elt.amount_currency
                all_vals = {}

            if elt.designation == 'Avoir Client':
                all_vals.update({
                    'name': elt.reference,
                    'partner_id': elt.partner.name,
                    # 'user_id': tracking_orders.user_id.name,
                    'amount_total': elt.amount_currency,
                    'debit': elt.amount_currency,
                    'credit': 0,
                    'libele': elt.libele_op or ' ',
                    'somme_paye': 0,
                    'solde': amount + elt.amount_currency,
                    # 'designation': str(elt.reference),
                    'designation': 'FACTURE',
                    'libele_op': ' ',
                    'create_date': elt.date.strftime('%d-%m-%Y'),
                })
                tbl.append(elt.reference)
                all_data.append(all_vals)
                print()
                print('All Data #3', all_data)
                print()
                amount += elt.amount_currency
                all_vals = {}

            """Paiements -"""
            if elt.designation == 'Paiement':
                all_vals.update({
                    'name': elt.reference,
                    'partner_id': elt.partner.name,
                    # 'user_id': tracking_orders.user_id.name,
                    'amount_total': elt.amount_currency,
                    'debit': 0,
                    'credit': elt.amount_currency,
                    'libele': elt.libele_op or ' ',
                    'somme_paye': 0,
                    'solde': amount + elt.amount_currency,
                    # 'designation': str(elt.reference),
                    'designation': 'PAIEMENT',
                    'libele_op': ' ',
                    'create_date': elt.date.strftime('%d-%m-%Y'),
                })
                tbl.append(elt.reference)
                print('TBL PAIEMENT', tbl)
                all_data.append(all_vals)
                print()
                print('All Data #4', all_data)
                print()
                amount += elt.amount_currency
                all_vals = {}

            """Encaissements -"""
            if elt.designation == 'Encaissement':
                all_vals.update({
                    'name': elt.reference or ' ',
                    'partner_id': elt.partner.name,
                    # 'user_id': tracking_orders.user_id.name,
                    'amount_total': elt.amount_currency,
                    'debit': 0,
                    'credit': elt.amount_currency,
                    'libele': elt.libele_op or ' ',
                    'somme_paye': 0,
                    'solde': amount + elt.amount_currency,
                    # 'designation': 'ENC-' + str(elt.reference),
                    'designation': 'ENCAISSEMENT',
                    'libele_op': ' ',
                    'create_date': elt.date.strftime('%d-%m-%Y'),
                })
                tbl.append(elt.reference)
                print('TBL ENCAISSEMENT', tbl)
                all_data.append(all_vals)
                print()
                print('All Data #5', all_data)
                print()
                amount += elt.amount_currency
                all_vals = {}

        tracking_partner = self.env['tracking.partner'].search([('id', '=', data.get('id'))])
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
        sheet.write(3, 7, past_amount_currency, cur_format)
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
        sheet.write(11, 7, past_amount_currency, currency_format)
        sheet.write(11, 9, past_amount_currency, currency_format)

        for elt in all_data:
            # print('data =', elt)
            # print(len(elt))
            # for x in elt:
            #     print('X =', x)
            sheet.write(index_data, 2, elt['create_date'], center)
            sheet.write(index_data, 3, elt['name'], center)
            sheet.write(index_data, 4, elt['designation'], center)
            sheet.write(index_data, 5, elt['libele'], center)
            sheet.write(index_data, 6, elt['libele_op'], center)
            sheet.write(index_data, 7, elt['debit'], currency_format)
            sheet.write(index_data, 8, elt['credit'], currency_format)
            sheet.write(index_data, 9, elt['solde'], currency_format)
            # sheet.write(index_data + 1, 7, (past_amount_currency), currency_format)
            # sheet.write(index_data + 1, 8, (total_somme + total_retour), currency_format)
            sheet.set_row(index_data, 20)
            sheet.set_row(index_data + 1, 20)
            print('Dernier index', index_data)
            index_data += 1
            sheet.write(index_data + 4, 5, 'SAUF ERREUR OU OMISSION, VOTRE SOLDE EST DE: ', bold)
            sheet.write(index_data + 4, 8, amount, currency_format2)
            sheet.write(index_data + 3, 3, '   ')
            sheet.write(index_data + 3, 4, '   ')
            sheet.write(index_data + 3, 5, '   ')
            sheet.write(index_data + 3, 6, '   ')
            sheet.write(index_data + 3, 7, '   ')
            sheet.write(index_data + 3, 8, '   ')
            sheet.set_row(index_data + 4, 20)
