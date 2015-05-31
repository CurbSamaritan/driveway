angular.module("curbsamplacard")
  .controller("PlacardCtrl", function($scope, code, project) {
    $scope.code = code;
    $scope.project = project
    $scope.shortnumber = $scope.project.phone.replace(/[^0-9]/g,'');
  });

