angular.module("curbsam")
  .controller("HistoryCtrl", function(session, GenericPopup, $scope, $q) {
    $scope.callerNames = {};
    $scope.calls = [];
    $scope.callers = {};
    $scope.pageCalls = [];
    $scope.pageSize = 10;
    $scope.pageChanged = function(currentPage) {
      if (currentPage >= 1) {
        var start = $scope.pageSize * (currentPage - 1)
        $scope.pageCalls = $scope.calls.slice(start, start + $scope.pageSize);
      }
    };

    var resetNames = function() {
      $scope.callerNames = {};
      $.map($scope.calls, function(call) {
        var caller = $scope.callers[call.caller];
        $scope.callerNames[call.caller] = caller && caller.nickname.value;
      });
    };

    session.onSigninChange($scope).on(function(user) {
      if (user.ready) {
        user.fetchCallers().then(function(callers) {
          $scope.callers = callers;
          resetNames();
        });
        user.onCalls($scope).on(function(calls) {
          $scope.calls = calls;
          resetNames();
          $scope.pageChanged(1);
        });
      }
    });

    $scope.rename = function(caller) {
      caller.nickname.set($scope.callerNames[caller.id]);
    };

    $scope.thank = function(call) {
      return GenericPopup.open({ 
        title: "Send a Thank-You", 
        body: "You can send your thanks to the person who texted you.",
        type : "textarea",
        required: true
      }).then(function (thankYouMessage) {
          call.thanked.do(thankYouMessage);
        });
    };

    $scope.report = function(call) {
      return GenericPopup.open({ 
        title: "Report an abusive text", 
        body: "Is the text rude, abusive, or inappropriate?  Please add any additional information below",
        type : "textarea",
        required: true
      }).then(function(reason) {
          call.reported.do(reason);
        });
    };
  })
;
