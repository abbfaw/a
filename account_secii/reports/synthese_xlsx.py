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
        all_date = []
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
        sale_order = self.env['sale.order'].sudo()
        purchase_order = self.env['purchase.order'].sudo()
        account_move = self.env['account.move'].sudo()
        account_move_line = self.env['account.move.line'].sudo()
        account_payment = self.env['account.payment'].sudo()
        secii_encaissement = self.env['secii.encaissement'].sudo()
        # retour = self.env['purchase.order'].sudo()
        print('partner_id', partner_id)

        """ Recherche des IDS de tous les modules """
        find_account_move_id = account_move.search(
            [('partner_id', '=', partner_id), ('invoice_date', '>=', start_date), ('invoice_date', '<=', end_date),
             ('state', '=', 'posted'), ('move_type', 'in', ('out_invoice', 'out_refund'))])
        for elt0 in find_account_move_id:
            all_date.append(elt0.invoice_date.strftime('%d-%m-%Y'))
        print('FActure', find_account_move_id)

        # find_account_move_line_id = account_move_line.search([('parent_state', '=', 'posted'), ('account_root_id', '=', 52049), ('date', '>=', start_date), ('date', '<=', end_date)])
        # find_account_move_line_id = account_move_line.search(
        #     [('partner_id', '=', partner_id), ('move_id', '=', 3), ('parent_state', '=', 'posted'), ('account_root_id', '=', 52049),
        #      ('date', '>=', start_date), ('date', '<=', end_date)])
        find_account_move_line_id = account_move_line.search(
            [('partner_id', '=', partner_id), ('move_id', '=', 3), ('parent_state', '=', 'posted'),
             ('account_id.code', '=', 411100),
             ('date', '>=', start_date), ('date', '<=', end_date)])
        for elt1 in find_account_move_line_id:
            all_date.append((elt1.date.strftime('%d-%m-%Y')))

        find_account_payment_id = account_payment.search(
            [('partner_id', '=', partner_id), ('date', '>=', start_date), ('date', '<=', end_date),
             ('state', '=', 'posted'), ('partner_type', '=', 'customer')])
        for elt2 in find_account_payment_id:
            all_date.append(elt2.date.strftime('%d-%m-%Y'))

        find_sale_order_id = sale_order.search(
            [('partner_id', '=', partner_id), ('date_effective', '>=', start_date), ('date_effective', '<=', end_date),
             ('is_prive', '=', True), ('state', '=', 'sale')])
        for elt3 in find_sale_order_id:
            all_date.append(elt3.date_effective.strftime('%d-%m-%Y'))

        find_purchase_order_id = purchase_order.search(
            [('partner_id', '=', partner_id), ('create_date', '>=', start_date), ('create_date', '<=', end_date),
             ('state', '=', 'purchase'), ('is_prive', '=', True), ('retour', '=', True), ])
        for elt4 in find_purchase_order_id:
            all_date.append(elt4.create_date.strftime('%d-%m-%Y'))

        find_secii_encaissement_id = secii_encaissement.search(
            [('partenaire', '=', partner_id), ('date', '>=', start_date), ('date', '<=', end_date),
             ('instance', '=', True), ('status', '=', 'paye')])
        for elt5 in find_secii_encaissement_id:
            all_date.append(elt5.date.strftime('%d-%m-%Y'))

        """concaténation de toutes les Dates"""

        # all_date = datetime.strptime(find_sale_order_id.mapped('date_effective'), ) + find_purchase_order_id.mapped(
        #     'create_date') + find_account_move_id.mapped('create_date') + find_account_payment_id.mapped(
        #     'date') + find_secii_encaissement_id.mapped('date_effective')
        # print('ALL DATE #0', all_date)

        def sortDates(datesList):
            split_up = datesList.split('-')
            return split_up[2], split_up[1], split_up[0]

        all_date.sort(key=sortDates)

        # test = sorted(all_date)
        print('ALL DATE #1\n', all_date)
        print('ALL DATE #0', type(all_date))

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
        for date in all_date:
            """Pièces comptables +"""
            for pc in find_account_move_line_id:
                tracking_pcomptables = tracking.search(
                    [('partner', '=', partner_id), ('date', '=', date), ('purchase_ref', '=', str(pc.id) + 'PC')])
                print('Tracking ------ PC ..', tracking_pcomptables)
                if tracking_pcomptables:
                    if tracking_pcomptables.purchase_ref not in tbl:
                        all_vals.update({
                            'name': tracking_pcomptables.reference,
                            'partner_id': tracking_pcomptables.partner.name,
                            'amount_total': tracking_pcomptables.amount_currency,
                            'debit': tracking_pcomptables.amount_currency,
                            'credit': 0,
                            'libele': tracking_pcomptables.libele_op or ' ',
                            'somme_paye': 0,
                            'solde': amount + tracking_pcomptables.amount_currency,
                            'designation': 'SOLDE INITIAL',
                            'libele_op': ' ',
                            'create_date': tracking_pcomptables.date.strftime('%Y-%m-%d'),
                        })
                        tbl.append(tracking_pcomptables.purchase_ref)
                        all_data.append(all_vals)
                        print()
                        print('All Data #0', all_data)
                        print()
                        amount += tracking_pcomptables.amount_currency
                        all_vals = {}

            """Ventes +"""
            for so in find_sale_order_id:
                tracking_orders = tracking.search(
                    [('partner', '=', partner_id), ('date', '=', date), ('purchase_ref', '=', str(so.id) + 'VEN')])
                print('Tracking ------ Orders ..', tracking_orders)
                if tracking_orders:
                    if tracking_orders.purchase_ref not in tbl:
                        all_vals.update({
                            'name': tracking_orders.reference,
                            'partner_id': tracking_orders.partner.name,
                            # 'user_id': tracking_orders.user_id.name,
                            'amount_total': tracking_orders.amount_currency,
                            'debit': tracking_orders.amount_currency,
                            'credit': 0,
                            'libele': ' ',
                            'somme_paye': 0,
                            'solde': amount + tracking_orders.amount_currency,
                            # 'designation': 'BL-' + str(tracking_orders.reference),
                            'designation': 'VENTE',
                            'libele_op': tracking_orders.libele_op or ' ',
                            'create_date': tracking_orders.date.strftime('%Y-%m-%d'),
                        })
                        tbl.append(tracking_orders.purchase_ref)
                        all_data.append(all_vals)
                        print()
                        print('All Data #1', all_data)
                        print()
                        amount += tracking_orders.amount_currency
                        all_vals = {}

            """Achats +"""
            for po in find_purchase_order_id:
                tracking_purchases = tracking.search(
                    [('partner', '=', partner_id), ('date', '=', date), ('purchase_ref', '=', str(po.id) + 'ACH')])
                print('Tracking ------ Purchases ..', tracking_purchases)
                if tracking_purchases:
                    if tracking_purchases.purchase_ref not in tbl:
                        all_vals.update({
                            'name': tracking_purchases.reference,
                            'partner_id': tracking_purchases.partner.name,
                            # 'user_id': tracking_orders.user_id.name,
                            'amount_total': tracking_purchases.amount_currency,
                            'debit': 0,
                            'credit': tracking_purchases.amount_currency,
                            'libele': tracking_purchases.libele_op or ' ',
                            'somme_paye': 0,
                            'solde': amount + tracking_purchases.amount_currency,
                            # 'designation': 'BL-' + str(tracking_purchases.reference),
                            'designation': "RETOUR D'ACHAT",
                            'libele_op': ' ',
                            'create_date': tracking_purchases.date.strftime('%Y-%m-%d'),
                        })
                        tbl.append(tracking_purchases.purchase_ref)
                        all_data.append(all_vals)
                        print()
                        print('All Data #2', all_data)
                        print()
                        amount += tracking_purchases.amount_currency
                        all_vals = {}

            """Factures +"""
            for am in find_account_move_id:
                tracking_factures = tracking.search(
                    [('partner', '=', partner_id), ('date', '=', date), ('move_id', '=', am.id),
                     ('partner_type', '=', 'customer')])
                print('Tracking ------ Factures ..', tracking_factures)
                if tracking_factures:
                    if tracking_factures.reference not in tbl:
                        all_vals.update({
                            'name': tracking_factures.reference,
                            'partner_id': tracking_factures.partner.name,
                            # 'user_id': tracking_orders.user_id.name,
                            'amount_total': tracking_factures.amount_currency,
                            'debit': tracking_factures.amount_currency,
                            'credit': 0,
                            'libele': tracking_factures.libele_op or ' ',
                            'somme_paye': 0,
                            'solde': amount + tracking_factures.amount_currency,
                            # 'designation': str(tracking_factures.reference),
                            'designation': 'FACTURE',
                            'libele_op': ' ',
                            'create_date': tracking_factures.date.strftime('%Y-%m-%d'),
                        })
                        tbl.append(tracking_factures.reference)
                        all_data.append(all_vals)
                        print()
                        print('All Data #3', all_data)
                        print()
                        amount += tracking_factures.amount_currency
                        all_vals = {}

            """Paiements -"""
            for ap in find_account_payment_id:
                tracking_payments = tracking.search(
                    [('partner', '=', partner_id), ('date', '=', date), ('payment_id', '=', ap.id),
                     ('partner_type', '=', 'customer')])
                print('Tracking ------ Payments ..', tracking_payments)
                if tracking_payments:
                    if tracking_payments.reference not in tbl:
                        all_vals.update({
                            'name': tracking_payments.reference,
                            'partner_id': tracking_payments.partner.name,
                            # 'user_id': tracking_orders.user_id.name,
                            'amount_total': tracking_payments.amount_currency,
                            'debit': 0,
                            'credit': tracking_payments.amount_currency,
                            'libele': tracking_payments.libele_op or ' ',
                            'somme_paye': 0,
                            'solde': amount + tracking_payments.amount_currency,
                            # 'designation': str(tracking_payments.reference),
                            'designation': 'PAIEMENT',
                            'libele_op': ' ',
                            'create_date': tracking_payments.date.strftime('%Y-%m-%d'),
                        })
                        tbl.append(tracking_payments.reference)
                        print('TBL PAIEMENT', tbl)
                        all_data.append(all_vals)
                        print()
                        print('All Data #4', all_data)
                        print()
                        amount += tracking_payments.amount_currency
                        all_vals = {}

            """Encaissements -"""
            for se in find_secii_encaissement_id:
                print('ENC ## 1', str(se.id) + 'ENC', se.num_seq)
                tracking_encaissements = tracking.search(
                    [('partner', '=', partner_id), ('date', '=', date), ('purchase_ref', '=', str(se.id) + 'ENC')])
                print('Tracking ------ Encaissements ..', tracking_encaissements)
                if tracking_encaissements:
                    if tracking_encaissements.reference not in tbl:
                        all_vals.update({
                            'name': tracking_encaissements.reference or ' ',
                            'partner_id': tracking_encaissements.partner.name,
                            # 'user_id': tracking_orders.user_id.name,
                            'amount_total': tracking_encaissements.amount_currency,
                            'debit': 0,
                            'credit': tracking_encaissements.amount_currency,
                            'libele': tracking_encaissements.libele_op or ' ',
                            'somme_paye': 0,
                            'solde': amount + tracking_encaissements.amount_currency,
                            # 'designation': 'ENC-' + str(tracking_encaissements.reference),
                            'designation': 'ENCAISSEMENT',
                            'libele_op': ' ',
                            'create_date': tracking_encaissements.date.strftime('%Y-%m-%d'),
                        })
                        tbl.append(tracking_encaissements.reference)
                        print('TBL ENCAISSEMENT', tbl)
                        all_data.append(all_vals)
                        print()
                        print('All Data #5', all_data)
                        print()
                        amount += tracking_encaissements.amount_currency
                        all_vals = {}
            print('AMT', amount)

        print('all_vals =>', all_vals)
        print('Tbl ===>', tbl)
        print('all_data ', all_data)
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
