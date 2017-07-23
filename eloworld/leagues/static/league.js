$("tr.player-row").hover(function () {
    var name = $(this).attr("id");
    $('tr.player-row').each(function(i, obj) 
        {
        var opp = $(this).attr("id");
        var r = records[name];
        if (r[opp] > 0)
            $('#' + opp).css("background-color","#CEE9CE");
        else if (r[opp] < 0)
            $('#' + opp).css("background-color","#FFB7B3");
        else if (r[opp] == 0)
            $('#' + opp).css("background-color","#9EE5FF");  
        else
            $('#' + opp).css("background-color","white"); 
        })
    $(this).css("background-color","#ddd");           
    }
    , function() {
        $('tr.player-row').each(function(i, obj) {
            $(this).css("background-color","white");
        });
    });
