angular.module("curbsam")
  .controller("HistoryCtrl", function(session, GenericPopup, $scope, $q) {
    $scope.calls = [];
    $scope.pageCalls = [];
    $scope.pageSize = 10;
    $scope.pageChanged = function(currentPage) {
      if (currentPage >= 1) {
        var start = $scope.pageSize * (currentPage - 1)
        $scope.pageCalls = $scope.calls.slice(start, start + $scope.pageSize);
      }
    };

    session.onSigninChange($scope).on(function(user) {
      if (user.ready) {
        $q.all([ user.fetchCallers(), user.fetchCalls() ])
          .then(function(args) {
            var callers = {}
            $.map(args[0], function(caller) {
              callers[caller.id] = caller;
              caller.calls = 0;
            });

            var calls = args[1];
            $.map(calls, function(call) {
              call.caller = callers[call.caller];
              call.caller.n_calls++;
            });
            $scope.calls = calls;
            $scope.pageChanged(1);
          });
      }
    });



    $scope.rename = function(caller) {
      return GenericPopup.open({ 
        title: "Rename a caller", 
        body: "Give this caller a name so you can recognize his calls.",
        type : "text",
        defaultValue: caller.nickname.value
      }) .then(function(name) {
          caller.nickname.set(name);
        });
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
