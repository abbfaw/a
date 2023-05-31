# -*- coding: utf-8 -*-
from odoo import http, tools, _
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db, Home, SIGN_UP_REQUEST_PARAMS
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
# from odoo.addons.payment_transfer.controllers.main import TransferController
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_users import SignupError

import werkzeug
import pprint
from werkzeug.exceptions import Forbidden

import logging

_logger = logging.getLogger(__name__)

# Shared parameters for all login/signup flows
SIGN_UP_REQUEST_PARAMS = {'db', 'login', 'debug', 'token', 'message', 'error', 'scope', 'mode',
                          'redirect', 'redirect_hostname', 'email', 'name', 'partner_id',
                          'password', 'confirm_password', 'phone', 'city', 'country_id', 'lang'}


class AuthSignupHomeInherit(AuthSignupHome):
    """Redirection après inscription vers la partie addresse"""

    def get_auth_signup_qcontext(self, **kw):
        qcontext = super(AuthSignupHomeInherit, self).get_auth_signup_qcontext(**kw)
        return qcontext


    @http.route('/web/signup_2', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup_2(self, *args, **kw):
        # modded = super(AuthSignupHomeInherit, self).web_auth_signup(*args, **kw)
        params = request.env['ir.config_parameter'].sudo().search([('key', '=', 'mediano_website.sms_on_register')])
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            qcontext.update({'phone': kw.get('phone')})
            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                if qcontext.get('phone'):
                    User = request.env['res.users']
                    user_sudo = User.sudo().search(
                        User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                    )
                    template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
                                               raise_if_not_found=False)
                    """Si l'utilisateur qui vient d'être créer existe et que le template existe"""
                    if user_sudo and template:
                        template.sudo().send_mail(user_sudo.id, force_send=True)
                # return self.web_login(*args, **kw)
                contact = request.env['res.partner']
                userid = contact.sudo().search([('email', '=', kw.get('login')), ('name', '=', kw.get('name'))])
                if userid:
                    userid.phone = qcontext.get('phone')
                    userid.from_web = True
                else:
                    userid.from_web = False
                """Partie ou l'utilisateur est rediriger"""
                return request.redirect('/shop/address?partner_id=%s' % userid.id)

            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    # def do_signup(self, qcontext):
    #     res = super(AuthSignupHomeInherit, self).do_signup(qcontext)
    #
    #     return res
