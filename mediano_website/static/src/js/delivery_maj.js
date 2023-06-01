odoo.define("mediano_website.delivery_maj", function (require){
    "use strict";

   //définition de la variable Ajax
   var ajax = require('web.ajax');
//
   var adresse = document.getElementById('adl');
   var showroom = document.getElementById('shwrm');

   var div_livr = document.getElementById('adl_div');
   var div_shwrm = document.getElementById('shwrm_div');
   var $carriers = $('#delivery_carrier input[name="delivery_type"]');

//    livraison = $('#adl');
//    divLivraison = $('#adl_div');
//    showroom = $('#shwrm');
//    divShowroom = $('#shwrm_div');

   //récupérer le nombre d'éléments dans le panier
   var Qty = sessionStorage.getItem("website_sale_cart_quantity");
   if (Qty > 0){
        document.getElementById("elt").innerHTML = Qty;
    }
   else {
        document.getElementById("elt").innerHTML = 0;
    }

   //Appel de la méthode RPC

//   livraison.click(function () {
//        if (livraison.val() == this.checked){console.log('Adresse de Livraison')}
//
//   })

   adresse.addEventListener('click', function() {
        var value = adresse.value;
        localStorage['radio1'] = this.checked;

        if (value == 'livraison') {
            console.log('Adresse de Livraion normale')
            adresse.checked = true;
            console.log('AC', adresse.checked)
            showroom.checked = false;
            console.log('SC', showroom.checked)
            ajax.jsonRpc('/shop/payment/delivery', 'call', {'adl': 1}).then(function(result){
            console.log('1er radio')
            if (result == 'adl'){
                  console.log('Actualisation de facturation')
                  $('#facturation').load('/shop/payment #facturation');
                  console.log('Actualisation Adresse de Livraison')
                  $('#adl_div').load('/shop/payment #adl_div');
                  console.log('Actualisation Prix de la livraison')
                  $('#delivery_carrier').load('/shop/payment #delivery_carrier');
                  console.log('Actualisation de la Div des prix')
                  $('.toggle_summary_div').load('/shop/payment .toggle_summary_div');
                  console.log('Actualisation de la Div des prix #2')
                  $('#amount_total_summary').load('/shop/payment #amount_total_summary');
            }
            console.log('LIVRAISON NORMALE')
            });
        } else {}
    });

    showroom.addEventListener('click', function() {
        var value = showroom.value;
        localStorage['radio2'] = this.checked;
//
        if (value == 'Showroom') {
            console.log('SHowRoom')

            showroom.checked = true;
            console.log('SC', showroom.checked)
            adresse.checked = false;
            console.log('AC', adresse.checked)
            ajax.jsonRpc('/shop/payment/delivery', 'call', {'adl': 2}).then(function(result){
            if (result == 'shwrm') {
//                $('#badge_vert').replaceWith('<span id="badge_vert" class="badge text-bg-secondary o_wsale_delivery_badge_price">Gratuit</span>');
                console.log('Actualisation de facturation #2')
                $('#facturation').load('/shop/payment #facturation');
                console.log('Actualisation Adresse de Facturation')
                $('#shwrm_div').load('/shop/payment #shwrm_div');
                console.log('Actualisation Prix de la livraison')
                $('#delivery_carrier').load('/shop/payment #delivery_carrier');
                console.log('Actualisation de la Div des prix #3')
                $('.toggle_summary_div').load('/shop/payment .toggle_summary_div');
                console.log('Actualisation de la Div des prix #4')
                $('#amount_total_summary').load('/shop/payment #amount_total_summary');
            }
            });
        } else {}
    });
});

