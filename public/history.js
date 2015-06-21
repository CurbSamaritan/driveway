angular.module("curbsam")
  .controller("HistoryCtrl", function(session, GenericPopup, $scope, $q) {
    var hc = this;
    hc.callerNames = {};
    hc.calls = [];
    hc.callers = {};
    hc.pageCalls = [];
    hc.pageSize = 10;
    hc.pageChanged = function(currentPage) {
      if (currentPage >= 1) {
        var start = hc.pageSize * (currentPage - 1)
        hc.pageCalls = hc.calls.slice(start, start + hc.pageSize);
      }
    };

    var resetNames = function() {
      hc.callerNames = {};
      angular.forEach(hc.calls, function(call) {
        var caller = hc.callers[call.caller];
        hc.callerNames[call.caller] = caller && caller.nickname.value;
      });
    };

    session.onSigninChange($scope).on(function(user) {
      if (user.ready) {
        user.fetchCallers().then(function(callers) {
          hc.callers = callers;
          resetNames();
        });
        user.onCalls($scope).on(function(calls) {
          hc.calls = calls;
          resetNames();
          hc.pageChanged(1);
        });
      }
    });

    hc.rename = function(caller) {
      caller.nickname.set(hc.callerNames[caller.id]);
    };

    hc.thank = function(call) {
      return GenericPopup.open({ 
        title: "Send a Thank-You", 
        body: "You can send your thanks to the person who texted you.",
        type : "textarea",
        required: true
      }).then(function (thankYouMessage) {
          call.thanked.do(thankYouMessage);
        });
    };

    hc.report = function(call) {
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
