# -*- coding: utf-8 -*-
{
    'name': "mediano_website",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    # 'depends': ['base', 'portal', 'web', 'contacts'],
    'depends': ['base', 'portal', 'web', 'contacts', 'purchase', 'website_sale', 'website_sale_delivery', 'portal', 'project', 'account_payment', 'payment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/home.xml',
        'views/register.xml',
        'views/views.xml',
        'views/short_cart_summary.xml',
        'views/address_on_payment.xml',
        'views/address_management.xml',
        'views/portal_my_home.xml',
        'views/inherit_res_partner.xml',
        'views/res_config.xml',
        'views/thk_you.xml',
        'views/recaptcha.xml',
        'views/pwdstrength.xml',
        #'views/change_price.xml',
        # 'views/snippet_options.xml',
        'views/commune_view.xml',
        # 'data/frais_de_livraison.xml',
        # 'data/confirmation_achat.xml',
        # 'data/reset.xml',
        # 'data/signup.xml',
        'data/commune.xml',
        'views/inherit_stock_action.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'mediano_website/static/src/js/delivery_maj.js',
            'mediano_website/static/src/js/pwdstrength.js',
            'mediano_website/static/src/js/toggle.js',
            'mediano_website/static/src/css/style.css',
            'mediano_website/static/src/css/pwdstrength.css',
            'mediano_website/static/fonts/material-icons.css',
            'mediano_website/static/src/css/toggle.css',
        ],
    }
}
