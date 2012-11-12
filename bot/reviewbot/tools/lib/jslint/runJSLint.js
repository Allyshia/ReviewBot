function runJSLint(pathToJSLint, fileContent, custom_options){

  load(pathToJSLint);

  options = {};

  // Accept custom values if calling program has provided them
  if(custom_options){
    for(var op in custom_options){
      custom = custom_options[op];
      if(custom === 'false'){
          options[op] = false;  
      }
      else if(custom === 'true'){
          options[op] = true;
      }
      else if((typeof custom) === 'number'){
          options[op] = custom;
      }
    }
  }

  var result = JSLINT(fileContent, options);

  if (result) {
    //print("no errors");
  }

  else {
    for (var i=0; i<JSLINT.errors.length; i++){
      if(JSLINT.errors[i]){
        print(JSLINT.errors[i].line+":"+JSLINT.errors[i].character+":"+
          JSLINT.errors[i].reason);
      }
    }
  }
}