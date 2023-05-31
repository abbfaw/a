# -*- coding: utf-8 -*-
import markupsafe
from odoo import http, tools, _
from odoo.addons.web.controllers.home import Home as WebHome
from odoo.http import request
# from twilio.rest import Client
import secrets
import requests
import json

import logging
import odoo
from odoo.addons.web.controllers.utils import ensure_db, _get_login_redirect_url
from odoo.addons.auth_signup.models.res_users import SignupError
import werkzeug
from werkzeug.urls import url_encode
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

SIGN_UP_REQUEST_PARAMS = {'db', 'login', 'debug', 'token', 'message', 'error', 'scope', 'mode',
                          'redirect', 'redirect_hostname', 'email', 'name', 'partner_id',
                          'password', 'confirm_password', 'city', 'country_id', 'lang', 'signup_email'}


class CheckUsers(http.Controller):

    @http.route(['/register'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def reg(self, **kw):
        uid = request.session.uid
        red = 'mediano_website.stepone'
        render_values = {}
        """Paramètre permettant de vérifier si la case envoi d'un
        sms à l'inscription est activer"""
        params = request.env['ir.config_parameter'].sudo().search([('key', '=', 'mediano_website.sms_on_register')])
        pwd = kw.get('password')
        cfrm_pwd = kw.get('confirm_password')
        """Uppercase, Lowercase, Digit, Special"""
        u, l, d, s = 0, 0, 0, 0
        special = '`,.~{}()[]/+_=-!@#$%^&*|\\\'":?'

        """Vérification : si l'utilisateur est connecté il sera rediriger"""
        if uid:
            return request.redirect("/shop")
        else:
            pass

        """étape 1 de l'inscription"""
        if 'stepone' in kw and request.httprequest.method == "POST":

            """Recherche du login du coté des utilisateurs"""
            if request.env["res.users"].sudo().search([("login", "=", kw.get("login"))]):
                """Si Erreur retourné ce meesage"""
                kw["error"] = markupsafe.Markup(
                    "<div class='alert alert-danger text-center'>Un autre utilisateur est déjà inscrit avec cette adresse électronique.</div>")
                render_values = {'error': kw["error"], 'csrf_token': kw.get('csrf_token'), 'login': kw.get('login')}

                return request.render('mediano_website.stepone', render_values)

            if pwd != cfrm_pwd:
                """Si le mdp est différent du cfrm mdp afficher ce meesage"""
                kw["error"] = markupsafe.Markup(
                    "<div class='alert alert-danger text-center'>Les mots de passe ne sont pas identiques. Veuillez les ressaisir</div>")
                render_values = {'error': kw["error"], 'csrf_token': kw.get('csrf_token'), 'login': kw.get('login')}

                return request.render('mediano_website.stepone', render_values)

            if len(pwd) == len(cfrm_pwd) < 8:
                """Si la longueur du mdp ou du cfrm mdp est inférieur a 8 : afficher ce meesage"""
                print('8 Charactères')
                """markupsafe.markup permets de rendre du html avec les controlleurs"""
                kw["error"] = markupsafe.Markup(
                    "<div class='alert alert-danger'>Le mot de passe doit contenir 8 caractères dont : <ul><li><b>une majuscule</b></li> <li><b>une minuscule</b></li>"
                    "<li><b>un chiffre</b></li><li><b>un caractère spécial (optionnel)</b></li> </div>")

                render_values = {'error': kw["error"], 'csrf_token': kw.get('csrf_token'), 'login': kw.get('login')}

                return request.render('mediano_website.stepone', render_values)

            if pwd == cfrm_pwd and len(pwd) == 8:
                """Si la longueur du mdp est égale à celle du cfrm mdp qui est égale a 8"""
                for i in pwd:
                    if i.isdigit():
                        d += 1
                    if i.islower():
                        l += 1
                    if i.isupper():
                        u += 1
                    if i in special:
                        s += 1

                if ((u >= 1 and l >= 1 and d >= 1) or (u >= 1 and l >= 1 and d >= 1 and s >= 1) and u + l + d == len(
                        pwd)):
                    """Condition 1"""
                    if params:
                        steptwo = 'mediano_website.steptwo'
                        render_values = {
                            'login': kw.get('login'),
                            'password': kw.get('password'),
                            'confirm_password': kw.get('confirm_password'),
                            'csrf_token': kw.get('csrf_token'),
                            'sms_on': True,
                        }
                    else:
                        steptwo = 'mediano_website.steptwo'
                        render_values = {
                            'login': kw.get('login'),
                            'password': kw.get('password'),
                            'confirm_password': kw.get('confirm_password'),
                            'csrf_token': kw.get('csrf_token'),
                            'sms_on': False,
                        }

                    return request.render(steptwo, render_values)
                else:
                    kw["error"] = markupsafe.Markup(
                        "<div class='alert alert-danger'>Le mot de passe doit contenir 8 caractères dont : <ul><li><b>une majuscule</b></li> <li><b>une minuscule</b></li>"
                        "<li><b>un chiffre</b></li><li><b>un caractère spécial (optionnel)</b></li> </div>")

                    render_values = {'error': kw["error"], 'csrf_token': kw.get('csrf_token'), 'login': kw.get('login')}
                    return request.render('mediano_website.stepone', render_values)

        return request.render(red, render_values)

    def generate_code(self):
        """Génération de code aléatoire"""
        code = secrets.token_hex(6)[:6]
        return code

    def check_email(self, **kw):
        uid = request.session.uid
        """Vérification si l'utilisateur est connecté le rediriger sur shop sinon passer"""
        if uid:
            return request.redirect("/shop")
        else:
            pass


class HomeInherit(WebHome):

    # def send_sms_twilio(self, numero, nom):
    #     account_sid = 'AC0eacc095b5eec03c72edcc0f5fe748ec'
    #     auth_token = '2c019396c313b3e1179028804a056454'
    #     client = Client(account_sid, auth_token)
    #     # number = ''.join(self.partner_id.phone.split(' '))
    #     print("Number", numero)
    #     # body = f"Votre code de vérification est {secret}. Merci de bien vouloir le saisir afin de " \
    #     #        f"finaliser votre inscription."
    #     body = f"Félicitation Mr/Mme {nom} inscription finalisée. Bienvenue chez Mediano"
    #     from_ = '+15108226061'
    #     to = "+2250757110861"
    #     try:
    #         message = client.messages.create(body=body, from_=from_, to=to)
    #         print(message.body, f"{nom}")
    #     except:
    #         print("Vérifiez votre numéro de telephone")

    # def recaptcha(self, key, rend):
    #     g_recaptcha = request.env['ir.config_parameter'].sudo().search([('key', '=', 'recaptcha_public_key')])
    #     secret = request.env['ir.config_parameter'].sudo().search([('key', '=', 'recaptcha_private_key')])
    #     """Recaptcha"""
    #     if g_recaptcha:
    #         client_key = key
    #         secret_key = secret.value
    #         captcha_data = {
    #             'secret': secret_key,
    #             'response': client_key
    #         }
    #         r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=captcha_data)
    #         response = json.loads(r.text)
    #         verify = response['success']
    #         if verify:
    #             pass
    #         else:
    #             values = request.params.copy()
    #             values['error'] = _("ReCaptcha invalide. Veuillez reprendre")
    #             return request.render(rend, values)
    #     else:
    #         pass

    @http.route('/web/login', type='http', auth="public")
    def web_login(self, redirect=None, **kw):
        """Correction pour la connexion automatique de OdooBot
            1ère methode : passer auth -> None à auth -> public
            2ᵉ méthode : voir après le not request.uid """

        print('######')
        ensure_db()
        login = ''
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        # so it is correct if overloaded with auth="public"
        if not request.uid:
            request.update_env(user=odoo.SUPERUSER_ID)

        # """2e methode"""
        # if request.env.uid is None:
        #     if request.session.uid is None:
        #         #pas d'utilisateur -> auth = public avec pour utilisateur spécifique l'utilisateur normal
        #         request.env["ir.http"]._auth_method_public()
        #     else:
        #         #auth = user
        #         request.update_env(user=request.session.uid)

        SIGN_UP_REQUEST_PARAMS.update({'phone'})
        # print('Update', SIGN_UP_REQUEST_PARAMS)
        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        email_activate = request.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'mediano_website.email_activate')])
        number_activate = request.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'mediano_website.number_activate')])

        if email_activate and number_activate:
            print('Connexion par E-mail', email_activate, 'Connexion par N° de Tél', number_activate)
            values['both'] = True
            # values['only_email'] = True
        elif number_activate:
            print('Connexion par N° de Tél', number_activate)
            values['only_number'] = True
        else:
            values['only_email'] = True
        print('#1')
        if request.httprequest.method == 'POST':
            if kw.get('login'):
                login = request.params['login']
            else:
                print('ERTTTT')
                check = request.env['res.users'].sudo().search([('phone_num', '=', kw.get('phone'))])
                # for rs in check:
                #     print('ZZZZZZ')
                login = check.login
            try:
                uid = request.session.authenticate(request.db, login, request.params['password'])
                request.params['login_success'] = True
                return request.redirect(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                if kw.get('login'):
                    if e.args == odoo.exceptions.AccessDenied().args:
                        values['error'] = _("Login ou mot de passe incorrect")
                    else:
                        values['error'] = e.args[0]
                else:
                    if e.args == odoo.exceptions.AccessDenied().args:
                        values['error1'] = _("Numéro de Téléphone ou mot de passe incorrect")
                    else:
                        values['error1'] = e.args[0]

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')
        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        super(HomeInherit, self).web_login(redirect=None, **kw)
        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    # def do_signup(self, qcontext):
    #     res = super(HomeInherit, self).do_signup(qcontext)
    #     return res

    # def get_auth_signup_qcontext(self, **kw):
    #     qcontext = super(HomeInherit, self).get_auth_signup_qcontext(**kw)
    #     return qcontext

    @http.route('/register/process', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup_2(self, *args, **kw):
        """Fonction pour la création d'un compte.
        Cette fonction vérifie que le numéro de tel
        est unique dans la base ainsi que sa longueur"""

        params = request.env['ir.config_parameter'].sudo().search([('key', '=', 'mediano_website.sms_on_register')])
        qcontext = self.get_auth_signup_qcontext()
        User = request.env['res.users']
        verify_phone = User.sudo().search([('phone_num', '=', kw.get('phone'))])
        phone_length = kw.get('phone')
        if verify_phone:
            qcontext['error'] = markupsafe.Markup(
                "<div class='alert alert-danger text-center'>Un autre utilisateur est déjà enregistrer avec ce numéro.</div>")
        if len(phone_length) != 10:
            qcontext['error'] = markupsafe.Markup(
                "<div class='alert alert-danger text-center'>Veuillez entrer un numéro de téléphone correct.</div>")

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                qcontext.update({'phone': kw.get('phone')})
                self.do_signup(qcontext)

                """Send an account creation confirmation email"""
                if qcontext.get('phone'):
                    # User = request.env['res.users']
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
                numero = userid.phone
                nom = userid.name
                """Envoi du SMS d'inscription"""
                if params:
                    self.send_sms_twilio(numero, nom)
                else:
                    pass
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

        response = request.render('mediano_website.steptwo', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        super(HomeInherit, self).web_auth_reset_password(*args, **kw)
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            response = kw['g-recaptcha-response']
            redirect = 'auth_signup.reset_password'
            self.recaptcha(response, redirect)
            try:
                if qcontext.get('token'):
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    login = qcontext.get('login')
                    assert login, _("No login provided.")
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        login, request.env.user.login, request.httprequest.remote_addr)
                    request.env['res.users'].sudo().reset_password(login)
                    qcontext['message'] = _("Password reset instructions sent to your email")
            except UserError as e:
                qcontext['error'] = e.args[0]
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        elif 'signup_email' in qcontext:
            user = request.env['res.users'].sudo().search(
                [('email', '=', qcontext.get('signup_email')), ('state', '!=', 'new')], limit=1)
            if user:
                return request.redirect('/web/login?%s' % url_encode({'login': user.login, 'redirect': '/web'}))

        response = request.render('auth_signup.reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response
