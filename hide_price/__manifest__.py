# -*- coding: utf-8 -*-
{
    'name': "Vitrine Web",

    'summary': """Masquer les prix sur le site web quand l'utilisateur n'est pas connecté""",

    'description': """Masquer les prix sur le site web""",

    'author': "YARD",
    'website': "http://www.progistack.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website_sale', 'website', 'website_sale_delivery', 'sale', 'contacts', 'uom'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/inherit_res_partner.xml',
        'views/address_management.xml',
        'data/commune.xml',
        'data/category_id.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
    'sequence': 1,

    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
