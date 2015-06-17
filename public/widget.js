angular.module("curbsam")
  .directive("signinRequired", function() {
    return {
	    restrict : 'AE',
      transclude: true,
      template : "<div ng-if=\"user.ready\" ng-transclude></div>",
      controller : function(session, SigninPopup, BusyPopup, $scope) {

        session.onSigninChange($scope).on(function(user) {
          $scope.user = user;
          if (user.pending) {
            BusyPopup.open();
            SigninPopup.close();
          } else if (user.ready) {
            BusyPopup.close();
            SigninPopup.close();
          } else {
            BusyPopup.close();
            SigninPopup.open();
          }
        });
      }
    };
  }).provider("SigninPopup", function() {
    var modalInstance = null;

    var close = function() {
      if (modalInstance) {
        modalInstance.close();
      }
      modalInstance = null;
    };

    return {
      "$get" : function(util, $modal) {
        return {
          close : close,
          open : function () {
            close();
            modalInstance = $modal.open({
              animation: true,
              controller: function(session, SigninPopup, $scope, $state) {
                $scope.cancel = function () {
                  $state.go('about');
                  SigninPopup.close();
                };
                $scope.networks = session.networks;
              },
              size: 'lg',
              backdrop: 'static',
              templateUrl: util.cdn('/signinPopup.html')
            });
          }
        }
      }
    };
  }).filter("truncate", function() {
    return function(s, n) {
      return (s && (s.length > n)) ? (s.substring(n-3) + "...") : s;
    };
  }).provider("GenericPopup", function() {
    return {
      "$get" : function(util, $modal) {
        return {
          open : function(options) {
            var modalInstance = $modal.open({
              animation: true,
              templateUrl: util.cdn('/genericPopup.html'),
              controller: function ($scope, $modalInstance) {
                $scope.options = options;
                $scope.response = options.defaultValue;
                $scope.ok = function(value) {
                  $modalInstance.close(value);
                };

                $scope.cancel = function () {
                  $modalInstance.dismiss('cancel');
                };
              },
              size: "sm"
            });
            return modalInstance.result;
          }
        };
      }
    };
  }).provider("BusyPopup", function() {
    return {
      "$get" : function(util, $modal) {
        var close = null;
        return {
          open : function() {
            var modalInstance = $modal.open({
              animation: true,
              templateUrl: util.cdn('/busyPopup.html'),
              size: "sm",
              backdrop: 'static',
              controller: function ($modalInstance) {
                close = function() {
                  $modalInstance.dismiss('cancel');
                };
              }
            });
          },
          close : function() {
            close && close();
          }
        };
      }
    };
  }).directive("csSocial", function(session) {
    return {
	    restrict : 'AE',
      controllerAs: 'soc',
      scope : {
        name : "=csSocial",
      },
      template : '<button ng-click="soc.signin(name)" class="zocial" ng-class="name">{{soc.titles[name]}}</button>',
      controller : function() {
        this.titles = {
          google : "Google" ,
          facebook : "Facebook"
        };
        this.signin = session.signin;
      }
    };
  }).directive("csAlert", function() {
    return {
	    restrict : 'AE',
      template : '<alert ng-if="theAlert.visible" type="{{theAlert.type || \'success\'}}" close="theAlert.visible=false">{{theAlert.content}}</alert>',
      scope : {
        theAlert : "=csAlert"
      }
    };
  }).filter("asPhoneNumber", function() {
    return function(n) {
      n = (n.charAt(1) === '1') ? n.substr(1) : n;
      return "1(" + n.substr(0,3) + ")" + n.substr(3,3) + "-" + n.substr(6);
    };
  }).controller('placardCtrl', function($scope) {
    $scope.openPlacard = function(code) {
      window.open('/placard/' + code, '_blank')
    };
  }).directive("csErrorable", function(util) {
    var img = new Image();
    img.src = util.cdn('/loading_bar.gif');
    return {
	    restrict : 'AE',
      transclude: true,
      controllerAs: 'err',
      controller : function() {
        this.image_url = img.src;
      },
      templateUrl: util.cdn('/errorable.html'),
      scope : {
        theError: "=csErrorable",
        theBusy: "=csErrorableBusy",
      }
    };
  })
;
