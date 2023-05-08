# -*- coding: utf-8 -*-
{
    'name': "open_view",

    'summary': """Ouvrir les vues des enregistrements présents dans tracking partner""",

    'description': """Ouvrir les vues des enregistrements présents dans tracking partner""",

    'author': "YARD",
    'website': "https://www.progistack.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_secii'],

    # always loaded
    'data': [
        'views/open_view.xml',
    ],

    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,

}
