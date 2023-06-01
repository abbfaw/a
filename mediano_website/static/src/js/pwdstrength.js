odoo.define("mediano_website.pwdstrength", function (require){
    "use strict";

    //définition de la variable Ajax
    var ajax = require('web.ajax');

    var allBars = document.querySelectorAll('div.progres-bar > div');
    var currentPercent = document.querySelector('div.pourcentage > div.digit');

    console.log('TEST #1')

    var inputPasswordField = document.querySelector('input.secupass');
    inputPasswordField.addEventListener('keyup', (e)=>{
        detPasswordStrength(inputPasswordField.value);
    });

    function detPasswordStrength(password){
        allBars.forEach(bar => {
            bar.style.background = 'none';
            bar.style.backgroundColor = '#bddfff';
        });
        var pwdPercent = getStrengthPercent(password);
        if(pwdPercent == 100){
            allBars.forEach(bar => {
                bar.style.background = 'green';
            });
        } else if(pwdPercent >= 75) {
            for(var i = 0; i < 3; i++){
                allBars[i].style.background = 'gold';
            }
        } else if(pwdPercent >= 50) {
            for(var i = 0; i < 2; i++){
                allBars[i].style.background = 'gold';
            }
        } else if(pwdPercent >= 25) {
            allBars[0].style.background = 'red';
        }

        //displayPercent(pwdPercent);
    }

    function getStrengthPercent(inputPassword){
        var percent = 0;
        percent = percent + percentByLength(inputPassword);
        percent = percent + (percentByUppercase(inputPassword));
        percent = percent + (percentByChar(inputPassword));
        percent = percent + (percentByNum(inputPassword));
        //percent = charRepitition(percent, inputPassword);

        return percent;
    }

    function percentByLength(inputPassword){
        if(inputPassword.length >= 8) return 25;
        else if(inputPassword.length >= 4) return 15;
        else if(inputPassword.length > 0) return 5;
        else return 0;
    }

    function percentByUppercase(inputPassword){
        var letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        var noOfUpperCase = [];

        inputPassword.split('').forEach(char => {
            if(letters.includes(char)) noOfUpperCase.push(char);
        });

        if(inputPassword.length - noOfUpperCase.length >= inputPassword.length) return 0;
        else if(inputPassword.length - noOfUpperCase.length >= 2) return 25;
        else if(inputPassword.length - noOfUpperCase.length >= 1) return 15;
        else return 0;
    }

    function percentByChar(inputPassword){
        var allChar = '`,.~{}()[]/+_=-!@#$%^&*|\\\'":?';
        var noOfChar = [];

        inputPassword.split('').forEach(char => {
            if(allChar.includes(char)) noOfChar.push(char);
        });

        if(inputPassword.length - noOfChar.length >= inputPassword.length) return 0;
        else if(inputPassword.length - noOfChar.length >= 1) return 25;
        else return 0;
    }

    function percentByNum(inputPassword){
        var allChar = '1234567890';
        var noOfChar = [];

        inputPassword.split('').forEach(char => {
            if(allChar.includes(char)) noOfChar.push(char);
        });

        if(inputPassword.length - noOfChar.length >= inputPassword.length) return 0;
        else if(inputPassword.length - noOfChar.length >= 1) return 25;
        else return 0;
    }


    const showPasswordBtn = document.querySelector('div.show-pass');
    showPasswordBtn.addEventListener('click', (event)=>{
        if(inputPasswordField.getAttribute('type') == "password") {
            inputPasswordField.setAttribute('type','text');
            showPasswordBtn.children[0].innerHTML = 'visibility_off';
        } else {
            inputPasswordField.setAttribute('type','password');
            showPasswordBtn.children[0].innerHTML = 'visibility';
        }
    });

    // Methode du 2e input //

    var allBarsConfirm = document.querySelectorAll('div.progres-bar-confirm > div');
    var currentPercent2 = document.querySelector('div.pourcentage-confirm > div.digit-confirm');

    var inputConfirmPasswordField = document.querySelector('input.secupass-confirm');
    inputConfirmPasswordField.addEventListener('keyup', (e)=>{
        detConfirmPasswordStrength(inputConfirmPasswordField.value);
    });

    function detConfirmPasswordStrength(password){
        allBarsConfirm.forEach(bar => {
            bar.style.background = 'none';
            bar.style.backgroundColor = '#bddfff';
        });
        var pwdPercent = getConfirmStrengthPercent(password);
        if(pwdPercent == 100){
            allBarsConfirm.forEach(bar => {
                bar.style.background = 'green';
            });
        } else if(pwdPercent >= 75) {
            for(var i = 0; i < 3; i++){
                allBarsConfirm[i].style.background = 'gold';
            }
        } else if(pwdPercent >= 50) {
            for(var i = 0; i < 2; i++){
                allBarsConfirm[i].style.background = 'gold';
            }
        } else if(pwdPercent >= 25) {
            allBarsConfirm[0].style.background = 'red';
        }

        //displayPercent(pwdPercent);
    }

    function getConfirmStrengthPercent(inputPassword){
        var percent = 0;
        percent = percent + percentConfirmByLength(inputPassword);
        percent = percent + (percentConfirmByUppercase(inputPassword));
        percent = percent + (percentConfirmByChar(inputPassword));
        percent = percent + (percentConfirmByNum(inputPassword));

        return percent;
    }

    function percentConfirmByLength(inputPassword){
        if(inputPassword.length >= 8) return 25;
        else if(inputPassword.length >= 4) return 15;
        else if(inputPassword.length > 0) return 5;
        else return 0;
    }

    function percentConfirmByUppercase(inputPassword){
        var letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        var noOfUpperCase = [];

        inputPassword.split('').forEach(char => {
            if(letters.includes(char)) noOfUpperCase.push(char);
        });

        if(inputPassword.length - noOfUpperCase.length >= inputPassword.length) return 0;
        else if(inputPassword.length - noOfUpperCase.length >= 2) return 25;
        else if(inputPassword.length - noOfUpperCase.length >= 1) return 15;
        else return 0;
    }

    function percentConfirmByChar(inputPassword){
        var allChar = '`,.~{}()[]/+_=-!@#$%^&*|\\\'":?';
        var noOfChar = [];

        inputPassword.split('').forEach(char => {
            if(allChar.includes(char)) noOfChar.push(char);
        });

        if(inputPassword.length - noOfChar.length >= inputPassword.length) return 0;
        else if(inputPassword.length - noOfChar.length >= 1) return 25;
        else return 0;
    }

    function percentConfirmByNum(inputPassword){
        var allChar = '1234567890';
        var noOfChar = [];

        inputPassword.split('').forEach(char => {
            if(allChar.includes(char)) noOfChar.push(char);
        });

        if(inputPassword.length - noOfChar.length >= inputPassword.length) return 0;
        else if(inputPassword.length - noOfChar.length >= 1) return 25;
        else return 0;
    }


    const showConfirmPasswordBtn = document.querySelector('div.show-pass-confirm');
    showConfirmPasswordBtn.addEventListener('click', (event)=>{
        if(inputConfirmPasswordField.getAttribute('type') == "password") {
            inputConfirmPasswordField.setAttribute('type','text');
            showConfirmPasswordBtn.children[0].innerHTML = 'visibility_off';
        } else {
            inputConfirmPasswordField.setAttribute('type','password');
            showConfirmPasswordBtn.children[0].innerHTML = 'visibility';
        }
    });

    //visibility icon login

    var inputLoginPasswordField = document.querySelector('input.secupass-login');
    const showLoginPasswordBtn = document.querySelector('div.show-pass-login');
    showLoginPasswordBtn.addEventListener('click', (event)=>{
        if(inputLoginPasswordField.getAttribute('type') == "password") {
            inputLoginPasswordField.setAttribute('type','text');
            showLoginPasswordBtn.children[0].innerHTML = 'visibility_off';
        } else {
            inputLoginPasswordField.setAttribute('type','password');
            showLoginPasswordBtn.children[0].innerHTML = 'visibility';
        }
    });

});