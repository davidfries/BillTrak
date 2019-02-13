window.document.onload=function(){
    var possibleMatches = new Array();
    $(function() {
        $("#autocomplete").autocomplete({
            source:function(request, response) {
                $.getJSON("http://localhost:5002/companies",{
                    q: request.term, // in flask, "q" will be the argument to look for using request.args
                }, function(data) {
                    response(data.matching_results); // matching_results from jsonify
                });
            },
            
            select: function(event, ui) {
                console.log(ui.item.value); // not in your question, but might help later
            }
        });
    })
    


};