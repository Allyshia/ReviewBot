function runJSLint(fileContent){

  load('jslint.js');

  options = {
        es5: true,
        evil: true,
        indent: 2,
        undef: true,
        white: true,
        predef:  [ "exports",
                   "GLOBAL",
                   "process",
                   "require",
                   "__filename",
                   "__dirname",
                   "setTimeout",
                   "clearTimeout",
                   "setInterval",
                   "clearInterval",
                   "module"       ] 
    };

  var result = JSLINT(fileContent, options);

  if (result) {
    print("no errors");
  }

  else {
   for (var i=0; i<JSLINT.errors.length; i++){
      print ("line : " + JSLINT.errors[i].line);
      print ("char : " + JSLINT.errors[i].character);
      print ("reason : " + JSLINT.errors[i].reason);
    }
  }
}