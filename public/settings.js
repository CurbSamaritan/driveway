angular.module("curbsam")
  .controller("SettingsCtrl", function(session, GenericPopup, growl, $scope) {


    session.onSigninChange($scope).on(function(user) {
      if (user && user.ready) {
        $scope.changes = {
          nickname : user.nickname.value
        };

        $scope.$watch("changes.nickname", function(nickname) {
          user.nickname.set(nickname).then(function() {
            growl.success("Your nickname has been changed.", {});
          }, function(reason) {
            growl.error("There was a problem changing your nickname: ", {});
          });
        });

        $scope.codeEntered = function(form) {
          clearAlerts();
          var code = form.code.$modelValue;
          if (code) {
            form.code.$setViewValue('');
            form.code.$render();
            user.confirmCode(code).then(function() {
              $scope.codeAlert = {
                content : "The code was accepted, your number has been changed.",
                visible : true
              };
            }, function() {
              $scope.codeAlert = {
                content : "The code was not accepted.  Please try again",
                type : 'danger',
                visible : true
              };
            });
          }
        };

        $scope.enterNumber = function() {
          GenericPopup.open({ 
            title: "Your mobile number",
            body: "Please give us your mobile number so we can text you.",
            type : "text",
            required: true
          }).then(function(number) {
              clearAlerts();
              if (number) {
                user.sendNumber(number)
                  .then(function() {
                    $scope.numberAlert = {
                      content : "We texted a code to that number.  When you get it, enter it below",
                      visible : true
                    };
                  }, function(reason) {
                    $scope.numberAlert = {
                      content : "There was a problem sending you a text: " + reason,
                      visible : true
                    };
                  });
              }
            });
        };
      }      
    });
  })
;
