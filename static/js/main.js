window.document.onload=function(){
    var possibleMatches = new Array();
    $.getJSON('http://localhost:5002/', function(data) {
      $.each(data, function(i){
        possibleMatches.push(data[i]);
      })
    
      $( "#tags" ).autocomplete({
        source: availableTags
      });
    });
    


};