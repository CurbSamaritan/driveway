angular.module("curbsam")
  .config(function(cdnProvider, $stateProvider, $urlRouterProvider) {
    var cdn = cdnProvider.$get();

	  $urlRouterProvider.otherwise('/about');
	  $stateProvider.state('about', {
		  url : '/about',
      controller: 'AboutCtrl',
		  templateUrl : cdn + '/about.html'
    }).state('home', {
		  url : '/home',
		  templateUrl : cdn + '/home.html'
    }).state('settings', {
		  url : '/settings',
      controller : "SettingsCtrl",
		  templateUrl : cdn + '/settings.html'
    }).state('history', {
		  url : '/history',
      controller : "HistoryCtrl",
		  templateUrl : cdn + '/history.html'
    });
    
  }).run(function(session,  $rootScope, $state) {
    if (!$state.$current.name) {
      $state.go('about', { replace : true });  // why is this necessary?
    }
    session.init();
  }).provider("util", function() {
    var makeFuture = function() {
      var watchers = [];
      var lastVal;
      var lastValSet = false;
      return {
        trigger : function(val) {
          lastValSet = true;
          lastVal = val;
          $.map(watchers,
                function(watcherPair) {
                  var v = watcherPair[0](val);
                  var on = watcherPair[1];
                  if (v && v.then) {
                    v.then(on, function() { on(); });
                  } else {
                    on(v);
                  }
                });
        },
        habit : {
          on : function(watcher) {
            if (lastValSet) {
              watcher(lastVal);
            }
            var future = makeFuture();
            watchers.push([ watcher, future.trigger]);
            return future.habit;
          }
        }
      };
    };

    var habit = function(scope, watchExpression) {
      /*
        a habit is a variation on a Promise except that:

        * instead of "then()" it has "on()"
        * the callback passed to "on()" (called the "the habit-function") can be fired any number of times
        * It is created with a watchExpression that is evaluated against a given scope; changes trigger the habit-function
        * the habit only lives in the scope -- when the scope dies, the habit dies
        * the return value of "on()" is... another habit, which will be invoked with the return value of the habit-function
        * if the return value of the habit-function is a promise, the next habit-function will get its resolved value
        * errors are not separately handled, the habit-function is invoked with no arguments

        */

      var future = makeFuture();
      
      scope.$watch(watchExpression, future.trigger);

      return future.habit;
    };

    return {
      "$get" : function(cdn) {
        return {
          habit : habit,
          cdn : function(path) {
            return cdn + path;
          }
        }
      }
    };
  }).provider("csHttp", function() {


    var makeReal = function(backend, components) {
      return backend +  components.join("/");
    };

    var makeFake = function(components, ispost) {
      if (ispost) {
        components.splice(1, 1);
      }
      return "/fake/" + components.join('.') + ".json";
    };





    return {
      "$get" : function($http, $q, backend) {

        var dataOf = function(d) {
          if (d.data.result === 'success') {
            return d.data.data;
          } else {
            return $q.reject(d.data.reason);
          }
        };

        var errorOf = function() {
          return $q.reject("io error");
        };


        var makeURL = function(components, ispost) {
          return backend ? makeReal(backend, components) : makeFake(components, ispost) ;
        };
        return {
          get : function() {
            return $http.get(makeURL($.makeArray(arguments))).then(dataOf, errorOf);
          },
          post : function() {
            var components = $.makeArray(arguments);
            var args = components.pop()
            return $http({ method: "post",
                           url : makeURL(components, true),
                           headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                           data: args && $.param(args)
                         }).then(dataOf, errorOf);
          }
        };
      }
    };
  }).provider("session", function() {

    var memoize = function(f) {
      var v;
      var called = false;
      return function() {
        if (!called) {
          v = f();
          called = true;
        }
        return v;
      };
    };


    var pendingUser = {
      id : -1,
      ready : false,
      pending : true
    };

    var signedoutUser = {
      id : -2,
      ready : false,
      pending : false
    };

    var user = pendingUser;
    
    return {
      "$get" : function(util, csHttp, social, $q, $state, $timeout) {

        var makeField = function(className, model, fieldName) {
          var view = {
            value : model[fieldName],
            set : function(newValue) {
              var args = {};
              args[fieldName] = newValue;
              return csHttp.post(className, model.id, args)
                .then(function(d) {
                  view.value = d[fieldName];
                  return d;
                });
            }
          };
          return view;
        };

        var makeActionField = function(className, model, fieldName, process) {
          var view = {
            value : model[fieldName],
            do : function(newValue) {
              return csHttp
                .post(className, model.id, fieldName, 
                      { value : newValue })
                .then(process || function(d) {
                  return d.value;
                }).then(function(value) {
                  view.value = value;
                });
            }
          };
          return view;
        };

        var makeCaller = function(c) {
          return {
            id : c.id,
            nickname : makeField("caller", c, "nickname"),
            blocked : makeActionField("caller", c, "blocked")
          };
        };


        var mapOver = function(f) {
          return function(a) {
            return $.map(a, f);
          };
        };

        var makeUser = function(d) {

          var calls = null;
          var callPromise = null;

          var makeCall = function(c) {
            return {
              caller : c.caller,
              ctype : c.ctype,
              when : c.when,
              message : c.message,
              reported : makeActionField("call", c, "reported"),
              thanked : makeActionField("call", c, "thanked", 
                                        function(tc) {
                                          calls.unshift(makeCall(tc));
                                          return true;
                                        })
            };
          };


          var u = {
            nickname : makeField("user", d, "nickname"),
            number : makeActionField("user", d, "number"),
            code : d.code,
            numberSent : d.numberSent,
            network : d.social_network,
            ready : true,
            sendNumber : function(number) {
              return csHttp.post("user", d.id, "sendNumber", { number : number })
                .then(function() {
                  u.numberSent = true;
                });
            },
            confirmCode : function(code) {
              return csHttp.post("user", d.id, "confirm", { code : code })
                .then(function(d) {
                  u.number.value = d.number;
                  u.numberSent = false;
                  return d;
                });
            },
            fetchCallers : memoize(function() {
              return csHttp.get("user", d.id, "callers").then(mapOver(makeCaller));
            }),
            fetchCalls : function() {
              if (!callPromise) {
                callPromise = csHttp.get("user", d.id, "calls")
                  .then(mapOver(makeCall))
                  .then(function(c) {
                    calls = c;
                    return calls;
                  });
              }
              return callPromise;
            }
          };
          return u;
        };


        var checkUser = function() {
          return csHttp.get("user").then(makeUser);
        };

        var signin = function(network, access_token) {
          return csHttp.post("user", 
                             "signin", 
                             {
                               network : network, 
                               access_token : access_token
                             }).then(makeUser);
        };

        var signout = function() {
          return csHttp.post("user", "signout", null).then(function() {
            user = signedoutUser;
          });
        }

        var init = function() {
          x = hello.init(social, {redirect_uri: 'redirect'});


          hello.on('auth.login', function(auth) {
            signin(auth.network, auth.authResponse.access_token).then(function(u) {
              user = u;
            }, function(reason) {
              user = signedoutUser;
              alert(reason);
            });
          });

          hello.on('auth.logout', function(auth) {
            signout().then(function() {
              user = signedoutUser;
              $state.go('about');
            });
          });
        };

        $timeout(function() {
          if (user.pending) {
            user = signedoutUser;
          }
        }, 5000);
          

        var resolveTo = function(v) {
          var q = $q.defer();
          q.resolve(v);
          return q.promise;
        };
        return {
          init : init,
          onSigninChange : function(scope) {
            return util.habit(scope, function() { 
              return user && user.id;
            }).on(function() {
              return user;
            });
          },
          checkUser : checkUser,
          signin : function(network) {
            hello(network).login();
          },
          signout : function() {
            user && hello(user.network).logout();
          },
          networks : [ "google", "facebook" ]
        };
      }
    };
  })
  .controller("HeaderCtrl", function(session, $scope, $state) {

    session.onSigninChange($scope).on(function(user) {
      $scope.signedIn = user.ready;
    });

    $scope.signout = session.signout;
    $scope.networks = session.networks;
  });
;
