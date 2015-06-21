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
<html class="fullheight">
<head>
<title>Curb Samaritan</title>
<link rel="stylesheet" href="%(lib)s/zocial/0/zocial.css"/>
<link rel="stylesheet" href="%(public.cdn)s/carbontoad.css"/>

<script src="%(lib)s/angular.js/1.3.15/angular.js"></script> 
<script src="%(lib)s/hellojs/1.6.0/hello.all.min.js"></script>
<script src="https://cdn.rawgit.com/720kb/angular-socialshare/dc70f51766fcb14ad83decab6a55e1d1ba7f1d60/dist/angular-socialshare.min.js"></script>

<script>
angular.module("curbsam", ['720kb.socialshare'])
%(values)s
;
</script>

<script src="%(public.cdn)s/map.js"></script>
<script src="%(public.cdn)s/widget.js"></script>
<script src="%(public.cdn)s/main.js"></script>
<script src="%(public.cdn)s/history.js"></script>
<style>
.nav, .pagination, .carousel, .panel-title a { cursor: pointer; }
</style>
</head>
<body ng-app="curbsam" class="fullheight">
<div ng-include="'%(public.cdn)s/main.html'" class="fullheight"></div>
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
