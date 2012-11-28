// Trigger the ReviewBot tools lightbox when clicking on the ReviewBot link
//  in the nav bar.
$("#reviewbot-link").click(function() {
    $.fetchReviewBotTools();
});

$.fetchReviewBotTools = function() {
    RB.apiCall({
        type: "GET",
        dataType: "json",
        data: {},
        url: "/api/extensions/reviewbotext.extension.ReviewBotExtension/tools/",
        success: function(response) {
           $.showToolLightBox(response); 
        }
    });
}

var dlg;

$.showToolLightBox = function(response){
    var tools = response["tools"];
    var modal = {
            title: "Review Bot",
        };
    //TODO : only create dialog once and clear its contents before popping up?
    dlg = $("<div/>")
        .attr("id", "reviewbot-tool-dialog")
        .appendTo("body")
        .html($("<div/>").attr("id", "dialogContent").attr("class", "modalbox-contents"))
        .trigger("ready");
   
    var toolList = $("<ul/>").attr("style", "list-style:none;")
    $.each(tools, function(index, tool){
        if(tool["enabled"] && tool["allow_run_manually"]){
            toolList.append(
                ($("<li/>")
                    .append($("<input/>")
                        .attr("id", "checkbox_"+index)
                        .attr("type", "checkbox"))
                    .append($("<label/>")
                        .attr("for", "checkbox_"+index)
                        .html(tool["name"]))
                )
            );
        }
    });
    
    if(toolList.children().length > 0) {
        $("#dialogContent").html("Installed tools:").append(toolList);
        modal.buttons = [
                $('<input type="button" value="Cancel"/>'),
                $('<input type="button"/>')
                    .val("Run Tools")
                    .click(function(e){
                        // run tool
                    }),
            ]
    } else {
        // if no tools were loaded, display message
        $("#dialogContent").html("No tools installed.");
        modal.buttons = [
                $('<input type="button" value="OK"/>'),
            ]
    }

    dlg.modalBox(modal);
}