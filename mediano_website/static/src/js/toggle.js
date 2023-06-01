email = $('#option1');
divEmail = $('#mail_');
telephone = $('#option2');
divTelephone = $('#phone_');

    email.click(function () {
        telephone.parent().removeClass('btn-primary').css('color', '#000');
        email.parent().addClass('btn-primary');
        divEmail.show();
        divTelephone.hide();
    });

    telephone.click(function () {
        email.parent().removeClass('btn-primary');
        telephone.parent().removeClass('btn-light').addClass('btn-primary').css('color', '#fff');
        divTelephone.show();
        divEmail.hide();
    });


//    commune = $('#commune');
//    commune.click(function (){
//        if (commune.val() != "") {
//            commune.removeClass('is-invalid');
//        }
//        else {
//            commune.addClass('is-invalid');
//        }
//    });
