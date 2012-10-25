function runJSLint(pathToJSLint, fileContent, options){

  load(pathToJSLint);

  var result = JSLINT(fileContent, options);

  if (result) {
    //print("no errors");
  }

  else {
   for (var i=0; i<JSLINT.errors.length; i++){
      print(JSLINT.errors[i].line+":"+JSLINT.errors[i].character+":"+JSLINT.errors[i].reason);
    }
  }
}