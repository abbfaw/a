# -*- coding: utf-8 -*-

{
    "name" : "Website Coming Soon | Website Maintenance | Under Construction",
    "version":"16.0.1",
    "license": "OPL-1",
    "support": "relief.4technologies@gmail.com",  
    "author" : "Relief Technologies",    
    "category": "Website/Website",
    "summary": "",
    "description": """
    """,
    "depends" : [        
                "website",
                "website_mass_mailing",        
                ],
    
    "application" : True,
    
    "data" : [
         "views/snippet.xml",
         "views/snippet_panel.xml",            
            ],            
    'assets': {
        'web.assets_frontend': [
            "/rt_website_coming_soon/static/src/scss/snippet.scss",
        ],
    },        
    "images": ["static/description/background.png",],    
    "auto_install":False,
    "installable" : True,
    "price": 0,
    "currency": "EUR"   
}
