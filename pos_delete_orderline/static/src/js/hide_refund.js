odoo.define('pos_hide_refund.NumpadWidget', function(require) {
    'use strict';

    const NumpadWidget = require('point_of_sale.NumpadWidget');
    const Registries = require('point_of_sale.Registries');
    const session = require('web.session');

    const PosHideRefundNumpadWidget = NumpadWidget => class extends NumpadWidget {
        // redefinition des methodes hasPriceControlRights() et hasManualDiscount() pour verifier si l'utilisateur connecté
        // n'est pas un administrateur alors glisser le bouton remise et prix
        get hasPriceControlRights() {
            const cashier =this.env.pos.user;
            return (
                (cashier.role == 'manager') &&
                !this.props.disabledModes.includes('price')
            );
        }
        get hasManualDiscount() {
            const cashier = this.env.pos.user;
            console.log('===========hasManuelDiscount called=============');
          
            const managerPromise = session.user_has_group('point_of_sale.group_pos_manager');
            const responsablePromise = session.user_has_group('pos_delete_orderline.group_pos_reponsable_user');
            const utilisateurPromise = session.user_has_group('point_of_sale.group_pos_user');
          
            Promise.all([managerPromise, responsablePromise, utilisateurPromise])
              .then(([manager, responsable, utilisateur]) => {
                console.log('=====manager======', manager, '=================');
                console.log('======repos=====', responsable, '=================');
                console.log('======uti=====', utilisateur, '=================');
                console.log(cashier);
                console.log("UN autre", utilisateur, !responsable, !manager);
          
                if (utilisateur && !responsable && !manager) {
                  $("#refund_button").hide();
                  $("#saleorderbutton").hide();
                  $("#customcashmovebutton").hide();
                  $("#headerbuttoninherit").hide();
                  console.log("=======utilisateur===");
                } else if (utilisateur && responsable && !manager) {
                  $("#refund_button").show();
                  $("#saleorderbutton").show();
                  console.log("=======responsable===");
                } else if (manager) {
                  $("#refund_button").show();
                  $("#saleorderbutton").show();
                  console.log("=======administrateur===");
                }
              })
              .catch((error) => {
                console.error(error);
                // Gérer les erreurs potentielles ici
              });
            // Le reste de votre code...

            if(cashier.role=="manager"){
                return true
            }
            return false
        } 
        changeMode(mode) {
            if (!this.hasPriceControlRights && mode === 'price') {
                return;
            }
            if (!this.hasManualDiscount && (mode === 'discount')) {
                return;
            }
            this.trigger('set-numpad-mode', { mode });
        }

    };

    Registries.Component.extend(NumpadWidget, PosHideRefundNumpadWidget);

    return PosHideRefundNumpadWidget;
 });