angular.module("curbsamplacard")
  .controller("PlacardCtrl", function($scope, code, project) {
    $scope.code = code;
    $scope.project = project
    $scope.shortnumber = $scope.project.phone.replace(/[^0-9]/g,'');
  })
  .directive("csQr", function() {
    return {
	    restrict : 'AE',
      link : function(scope, element, attrs) {
        attrs.$observe('csQr', function(message) {
          $(element).qrcode(message);
        });
      }
    };
  })
;

