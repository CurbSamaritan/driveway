import types
import json

def flatten(d):
    rv =  [ ]
    for k, v in d.items():
        if type(v) == types.DictType:
            d1 = flatten(v)
            for k1, v1 in d1:
                rv.append((((k,) + k1), v1))
        else:
            rv.append(( (k,), v ))
    return rv

def alive(d):
    return { ".".join(map(str,k)): v for k,v in flatten(d) }


def renderPage(config, page, additionalValues={}):
    flatVals = alive(config)
    flatVals['values'] = "\n".join([ """.value("%s", %s)""" % (k, json.dumps(v)) 
                                     for k,v in (config['public'].items() + additionalValues.items() ) ])
    return page % flatVals

def renderRedirect(config):    
    return renderPage(config, '''
<!doctype html>
<html>
  <head> <script src="%(lib)s/hellojs/1.6.0/hello.all.min.js"></script> </head>
  <body></body>
</html>''')


def renderIndex(config):
    return renderPage(config, '''
<!doctype html>
<html>
<head>
<title>Curb Samaritan</title>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css"/>
<link rel="stylesheet" href="%(lib)s/bootstrap-social/4.9.0/bootstrap-social.min.css"/>
<link rel="stylesheet" href="%(lib)s/font-awesome/4.3.0/css/font-awesome.min.css"/>
<link rel="stylesheet" href="https://cdn.rawgit.com/vitalets/angular-xeditable/0b26f8859/dist/css/xeditable.css"/>

<script src="%(lib)s/jquery/2.1.4/jquery.min.js"></script>
<script src="%(lib)s/angular.js/1.3.15/angular.js"></script> 
<script src="%(lib)s/angular-ui-router/0.2.15/angular-ui-router.min.js"></script> 
<script src="%(lib)s/angular-ui-bootstrap/0.13.0/ui-bootstrap-tpls.min.js"></script>
<script src="%(lib)s/hellojs/1.6.0/hello.all.min.js"></script>
<script src="https://cdn.rawgit.com/vitalets/angular-xeditable/0b26f8859/dist/js/xeditable.min.js"></script>


<script>
angular.module("curbsam", ['ui.bootstrap', 'ui.router', 'xeditable'])
%(values)s
;
</script>

<script src="%(public.cdn)s/main.js"></script>
<script src="%(public.cdn)s/widget.js"></script>
<script src="%(public.cdn)s/about.js"></script>
<script src="%(public.cdn)s/history.js"></script>
<script src="%(public.cdn)s/settings.js"></script>
<style>
.nav, .pagination, .carousel, .panel-title a { cursor: pointer; }
</style>
</head>
<body ng-app="curbsam">
<div ng-include="'%(public.cdn)s/main.html'"></div>
</body>
</html> ''')
    

def renderPlacard(config, code):
    return renderPage(config, '''
<!doctype html>
<html>
<head>
<title>Curb Samaritan Placard</title>
    <script src="%(lib)s/jquery/2.1.4/jquery.min.js"></script>
    <script src="%(lib)s/angular.js/1.3.15/angular.js"></script> 
    <script src="https://cdn.rawgit.com/jeromeetienne/jquery-qrcode/2b253c5/jquery.qrcode.min.js"></script> 
<script>
angular.module("curbsamplacard", [])
%(values)s
;
</script>
<script src="%(public.cdn)s/placard.js"></script>

</head>
<body ng-app="curbsamplacard">
<div ng-include="'%(public.cdn)s/placard.html'"></div>
</body>
</html> ''', { "code" : code })
