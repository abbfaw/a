# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError


class HrEmployer(models.Model):
    _inherit = "hr.employee"

    taux_commission = fields.Float(string='Taux de commission')
    # societe = fields.Many2one('res.partner', string="Assigné à")
    # vendeur = fields.Many2one('res.partner', string="Vendeur", related='user_id.vendeur')


class ContactButton(models.Model):
    _inherit = "res.partner"

    vendor_order_count = fields.Char(compute='_compute_vendor_order_count')
    actual_partner = fields.Integer()  # This custom field.
    user_id_old = fields.Integer()  # This custom field.
    #hangement = fields.Boolean()
    #recuperer l'employée actuellement connecté
    def _get_actual_user(self):
        user = self.env['hr.employee'].search([
            ('user_id', '=', self.user_id.id)])
        return user.id

    def write(self, vals):
        if vals.get('active') is False:
            # DLE: It should not be necessary to modify this to make work the ORM. The problem was just the recompute
            # of partner.user_ids when you create a new user for this partner, see test test_70_archive_internal_partners
            # You modified it in a previous commit, see original commit of this:
            # https://github.com/odoo/odoo/commit/9d7226371730e73c296bcc68eb1f856f82b0b4ed
            #
            # RCO: when creating a user for partner, the user is automatically added in partner.user_ids.
            # This is wrong if the user is not active, as partner.user_ids only returns active users.
            # Hence this temporary hack until the ORM updates inverse fields correctly.
            self.invalidate_cache(['user_ids'], self._ids)
            users = self.env['res.users'].sudo().search([('partner_id', 'in', self.ids)])
            if users:
                if self.env['res.users'].sudo(False).check_access_rights('write', raise_exception=False):
                    error_msg = _('You cannot archive contacts linked to an active user.\n'
                                  'You first need to archive their associated user.\n\n'
                                  'Linked active users : %(names)s', names=", ".join([u.display_name for u in users]))
                    action_error = users._action_show()
                    raise RedirectWarning(error_msg, action_error, _('Go to users'))
                else:
                    raise ValidationError(_('You cannot archive contacts linked to an active user.\n'
                                            'Ask an administrator to archive their associated user first.\n\n'
                                            'Linked active users :\n%(names)s',
                                            names=", ".join([u.display_name for u in users])))
        # res.partner must only allow to set the company_id of a partner if it
        # is the same as the company of all users that inherit from this partner
        # (this is to allow the code from res_users to write to the partner!) or
        # if setting the company_id to False (this is compatible with any user
        # company)
        if vals.get('website'):
            vals['website'] = self._clean_website(vals['website'])
        if vals.get('parent_id'):
            vals['company_name'] = False
        if 'company_id' in vals:
            company_id = vals['company_id']
            for partner in self:
                if company_id and partner.user_ids:
                    company = self.env['res.company'].browse(company_id)
                    companies = set(user.company_id for user in partner.user_ids)
                    if len(companies) > 1 or company not in companies:
                        raise UserError(
                            ("The selected company is not compatible with the companies of the related user(s)"))
                if partner.child_ids:
                    partner.child_ids.write({'company_id': company_id})
        result = True
        # recuperer ancienne valeur
        c = self.user_id
        d = self.id
        print('d ==', d)
        # print('c ==', c)
        vals['user_id_old'] = c.id
        vals['actual_partner'] = d
        # vals['changement'] = True
        # print('==>', vals['user_id_old'])
        print('==>', vals['actual_partner'])

        # To write in SUPERUSER on field is_company and avoid access rights problems.
        if 'is_company' in vals and self.user_has_groups('base.group_partner_manager') and not self.env.su:
            result = super(ContactButton, self.sudo()).write({'is_company': vals.get('is_company')})
            del vals['is_company']
        result = result and super(ContactButton, self).write(vals)
        for partner in self:
            if any(u.has_group('base.group_user') for u in partner.user_ids if u != self.env.user):
                self.env['res.users'].check_access_rights('write')
            partner._fields_sync(vals)
        return result

    # @api.onchange('team_id')
    # def get_old_enc(self):
    #     print('actual_partner =', self.actual_partner)
    #     print('commercial =', self.user_id_old)
    #
    #     var = self.env['secii.encaissement'].sudo().search(
    #         [('partenaire', '=', self.actual_partner), ('commercial', '=', self.user_id_old)])
    #     print('rttttt', var)
    #     if var:
    #         print('')
        #     var.write({'old_com': self.actual_partner})
        #     print('Société rattaché avec succès')
        # else:
        #     pass

    # @api.onchange('user_id')
    # def _get_old_user(self):
    #     # old_partner = self.user_id_new.id
    #     print('old_partner', self.user_id_old.id)
    # # ---------------------------------
    #
    # self.user_id_new = self.user_id.id
    # print('self.user_id_new', self.user_id_new)
    # # ---------------------------------
    #
    # self.user_id_old = old_partner
    # print('user_id_old', self.user_id_old)
    # # ---------------------------------
    # rec = self.env['res.users'].sudo().browse(self.user_id).id
    # print(rec)

    # Avoir l'ID de l'utilisateur connecté
    # def _get_actual_partenaire(self):
    #     context = self._context
    #     current_uid = context.get('uid')
    #     user = self.env['hr.employee'].search([
    #         ('user_id', '=', current_uid)])
    #     return user.id

    # fonction pour compter les ventes d'un commercial
    # @api.depends('vendor_order_count')
    def _compute_vendor_order_count(self):
        for rec in self:
            rec.vendor_order_count = self.env['secii.encaissement'].search_count(
                [('commercial', '=', self._get_actual_user()),
                 ('status', 'in', ('encaisse', 'comptabilise'))])
            # self.env['res.partner'].sudo().search([('partenaire', '=', rec.commercial.user_id.id)])

    # fonction pour ouvrir la vue liste des commerciaux
    def open_view(self):
        print('Work')
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'name': _('Commerciaux'),
            'res_model': 'secii.encaissement',
        }
        domain = [('commercial', '=', self._get_actual_user()), ('status', 'in', ('encaisse', 'comptabilise'))]
        # action['view_id'] = self.env.ref('barcode.view_barcode_inventory_open').id
        action['domain'] = domain
        return action

    def show_report_client(self):
        action = {'type': 'ir.actions.act_window',
                  'name': 'Relevé Client', 'view_mode': 'tree,form',
                  'view_type': 'form',
                  'res_model': 'secii.synthese',
                  'view_id': False
                  }
        domain = [('client', '=', self.id)]
        action['domain'] = domain
        return action
