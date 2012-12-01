// Trigger the ReviewBot tools lightbox when clicking on the ReviewBot link
//  in the nav bar.

var dlg;
var modal;

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
            if(!dlg){
                $.createToolLightBox();
            }
            $.showToolLightBox(response); 
        }
    });
}

$.createToolLightBox = function() {
    modal = {
            title: "Review Bot",
        };
    dlg = $("<div/>")
        .attr("id", "reviewbot-tool-dialog")
        .attr("class", "modalbox-contents")
        .appendTo("body")
}

$.showToolLightBox = function(response) {
    var tools = response["tools"];
    var toolList = $("<ul/>").attr("style", "list-style:none;")

    $.each(tools, function(index, tool){
        if(tool["enabled"] && tool["allow_run_manually"]){
            toolList.append(
                ($("<li/>")
                    .append($('<input type="checkbox"/>')
                        .attr("id", "checkbox_"+index)
                        .attr("class", "toolCheckbox")
                        .attr("checked", "checked")
                        .change(function() {
                            var allChecked = 
                                ($(".toolCheckbox:checked").length > 0);
                            $("#button_run").attr("disabled", !allChecked);
                        }))
                    .append($("<label/>")
                        .attr("for", "checkbox_"+index)
                        .html(tool["name"]))
                )
            );
        }
    });

    if(toolList.children().length > 0) {
        dlg
            .text("Installed tools:")
            .append(toolList);
        modal.buttons = [
            $('<input id="button_cancel" type="button" value="Cancel"/>'),
            $('<input id="button_run" type="button"/>')
                .val("Run Tools")
                .click(function(e){
                    // run tool
                }),
        ];
    } else {
        // if no tools were loaded, display message
        dlg.text("No tools installed.");
        modal.buttons = [
            $('<input id="button_ok" type="button" value="OK"/>'),
        ];
    }

    dlg.modalBox(modal);
}