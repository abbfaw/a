# -*- coding: utf-8 -*-
{
    'name': "Caisse",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Progistack",
    'website': "https://www.progistack.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'hr', 'contacts', 'sale', 'purchase', 'report_xlsx', 'account_accountant', 'stock'],

    # always loaded
    'data': [
        'security/secci_security.xml',
        'security/secii_commercial_access.xml',
        # 'security/secii_sale_security.xml',
        'security/ir.model.access.csv',
        'views/sequence_agentis.xml',
        'views/encaissement_menu.xml',
        'views/commission_menu.xml',
        'views/secii_comptable_view.xml',
        'views/sequence_encaissement.xml',
        'views/box_yop_view.xml',
        'views/yop_sequence.xml',
        'views/sequence_encaissement.xml',
        # 'views/rapport_secii_view.xml',
        'views/secii_whatsapp_view.xml',
        'reports/partner_synthese_report.xml',
        'sale_view/inherit_purchase_order_view.xml',
        'sale_view/inherit_res_partner.xml',
        'sale_view/inherit_sale_order_view.xml',
        'sale_view/inherit_stock_picking.xml',

        'sale_view/sale_dashboard.xml',

        'views/synthese_secii_view.xml',
        'views/plafond.xml',
        'suivi_view/facture.xml',
        'suivi_view/encaissement.xml',
        'suivi_view/ventes.xml',
        'suivi_view/tracking_instance_partner.xml',
        'suivi_view/sequence_encaissement.xml',
        'suivi_view/charge_partner.xml',
        'suivi_view/stock_move_view.xml',
        'suivi_view/purchase_order_view.xml',
        # 'views/dashboard.xml',
    ],

    # "external_dependencies": {"python": ["date_utils"]},

    'assets': {
        'web.assets_backend': [
            # 'account_secii/static/src/js/**/*'
            "account_secii/static/src/js/secii_box_dashbord.js",
            "account_secii/static/src/js/yop_dashboard.js"
            # "account_secii/static/src/js/action_excel.js"
        ],

        'web.assets_qweb': [
            # 'account_secii/static/src/xml/**/*'
            'account_secii/static/src/xml/secii_box_dashbord.xml',
            'account_secii/static/src/xml/yop_dashboard.xml',

        ]

    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,

}
