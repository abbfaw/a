odoo.define('pos_delete_orderline.chrome', function (require) {
    "use strict";
    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');
    const session = require('web.session')

    
    const managerPromise = session.user_has_group('point_of_sale.group_pos_manager');
    const responsablePromise = session.user_has_group('pos_delete_orderline.group_pos_reponsable_user');
    const utilisateurPromise = session.user_has_group('point_of_sale.group_pos_user');
  
    Promise.all([managerPromise, responsablePromise, utilisateurPromise])
      .then(([manager, responsable, utilisateur]) => {
        console.log('=====manager======', manager, '=================');
        console.log('======repos=====', responsable, '=================');
        console.log('======uti=====', utilisateur, '=================');

    const PosEmployee = (Chrome) => class extends Chrome {
            get headerButtonIsShown(){
                console.log('===========headerButtonIsShown called=============');
                if (this.env.pos.get_cashier().role == 'manager'){
                    return true;
                }
                else if(this.env.pos.get_cashier().role == 'cashier'){
                    return true;
                }
                return false;
            }
            showCashMoveButton() {
                if (manager){
                    return super.showCashMoveButton() && manager
                }
                else if(manager && !responsable){
                    return super.showCashMoveButton() && manager && !responsable ;
                }
                else if(manger && !responsable && !manager){
                    return super.showCashMoveButton() && manager && !responsable;
                }
            }
            
        };
    })
    .catch((error) => {
        console.error(error);
        // Gérer les erreurs potentielles ici
      });
    // Le reste de votre code...
    Registries.Component.extend(Chrome, PosEmployee);

    return Chrome;
});