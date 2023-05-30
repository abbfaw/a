odoo.define('pos_hide_refund.NumpadWidget', function(require) {
    'use strict';

    const NumpadWidget = require('point_of_sale.NumpadWidget');
    const Registries = require('point_of_sale.Registries');

    const PosHideRefundNumpadWidget = NumpadWidget => class extends NumpadWidget {
         mounted() {
                this.env.pos.on('change:cashier', () => {
                    const cashier = this.env.pos.user;
                    if (cashier.role!= 'manager'){
                        $("#refund_button" ).hide();
                    }else{
                        $("#refund_button" ).show();
                    }
                })
         }

        willUnmount() {
            this.env.pos.on('change:cashier', null, this);
            const cashier = this.env.pos.user;
            if (cashier.role!= 'manager') {
                $("#refund_button" ).hide();
            }
        }
        // redefinition des methodes hasPriceControlRights() et hasManualDiscount() pour verifier si l'utilisateur connecté
        // n'est pas un administrateur alors glisser le bouton remise et prix
        get hasPriceControlRights() {
            const cashier =this.env.pos.user;
            if (cashier.role != 'manager') {
                $("#refund_button" ).hide();
            };
            return (
                (cashier.role == 'manager') &&
                !this.props.disabledModes.includes('price')
            );
        }
        get hasManualDiscount() {
            // Vérifier si l'utilisateur connecté est un manager
            const cashier = this.env.pos.user;
            console.log(cashier)
            $("#saleorderbutton" ).show();
            if (cashier.role != 'manager'){
                $("#refund_button" ).show();
                return false;
            }
            else{
                $("#refund_button" ).show();
                return true;
            }
        }
        changeMode(mode) {
            const cashier = this.env.pos.user;
            const userGroups = cashier.groups_id;
            if (cashier.role != 'manager'){
                $("#refund_button" ).hide();
            }
            if (!this.hasPriceControlRights && mode === 'price') {
                return ;
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