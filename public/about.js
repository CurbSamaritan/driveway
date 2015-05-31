angular.module("curbsam")
  .controller("AboutCtrl", function(session, cdn, $scope) {
    session.onSigninChange($scope).on(function(user) {
      $scope.isSignedIn = !!user;
    });

    $scope.cdnPath = function(path) {
      return cdn + path;
    };
  })
;
