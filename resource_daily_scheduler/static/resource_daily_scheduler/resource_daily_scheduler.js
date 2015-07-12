function msIeVersion() {
    var ua = window.navigator.userAgent;
    var msie = ua.indexOf("MSIE ");

    if (msie > 0)      // If Internet Explorer, return version number
        return (parseInt(ua.substring(msie + 5, ua.indexOf(".", msie))));
//    else                 // If another browser, return 0
//        alert('otherbrowser');

    return false;
}

function isDialogSupported(){
    //return false;
    var ieVer = msIeVersion();
    if(ieVer && ieVer<9) return false;
    return true;
}

function addResourceClicked()
{
    //$(window.location).attr('href', '/normal_admin/resource_daily_scheduler/bookableresource/add/');

    var ieVer = msIeVersion();
    if(!isDialogSupported()){
        redirectToUrl('create_resource/');
        return;
    }

    $( "#dialog" ).dialog("open");
//    $("#newResourceFormSubmit").click(function(){
//
//    });
}

function isApprover(){
    return isAdmin;
}

function hasCreatePermission(){
    return isAdmin;
}

var gTodoLegend = ["Waiting for your approval", "Approved, you can change"//, "Ongoing"
];


function isTodoItem(legendText){
    for(var index in gTodoLegend){
            if(legendText==gTodoLegend[index])
                return true
    }
    return false;
}


$(function() { // document ready
    $('.datepicker').datepicker();
//    $(".fc-time").hide();

    $( "#dialog" ).dialog({"width": "800px", "autoOpen": false});
    $( "#newBookingReqDialog" ).dialog({"width": "800px", "autoOpen": false});
    $( "#bookingReqEditDialog" ).dialog({"width": "800px", "autoOpen": false});

    $( "#dialog-confirm" ).dialog({
      resizable: false,
      autoOpen: false,
      //height:140,
      modal: true
    });

    $('#newResourceForm').ajaxForm({
        success: function(data){
            if(data.pk){
                $( "#dialog" ).dialog("close");
                $('#calendar').fullCalendar(
                            'addResource',
                            { title: data.title, id: data.pk },
                            true // scroll to the new resource?
                );
                $('#id_resource').append('<option value="'+data.pk+'">'+data.title+'</option>')
            }
            else{//Create error
                alert("Create error, please contact admin!")
            }
        },
        error: function(a,b,c){
//                console.log("Create error");
            alert("Create error, please contact admin!")
        }
    });

    $('#newBookingReqForm').ajaxForm({
        success: function(data){
            if(data.pk){
                $( "#newBookingReqDialog" ).dialog("close");

                location.reload();
            }
            else{//Create error
                alert("Create error, please contact admin!")
            }
        },
        error: function(a,b,c){
//                console.log("Create error");
            alert("Create error, please contact admin!")
        }
    });

//    $("#draft").css("background-color", notApprovedRequestColor);
//    $("#approved").css("background-color", approvedRequestColor);
//    $("#ongoing").css("background-color", ongoingRequestColor);

    if(hasCreatePermission()){
        $('.fc-toolbar .fc-left').prepend(
            $('<button type="button" class="fc-button fc-state-default fc-corner-left fc-corner-right">+ Resource</button>')
                .on('click', function() {
                    addResourceClicked();
                })
        );
    }

    $('#bookingReqEditForm').ajaxForm({
        success: function(data){
            if(data.pk){
//                $("#id_update-end").datepicker("hide");
//                $("#id_update-start").datepicker("hide");
//                $('#ui-datepicker-div').hide();
//                $("#id_update-start").blur();
//                $("#id_update-end").blur();
//                $("id_project").focus();
                $( "#bookingReqEditDialog" ).dialog("close");
//                $('#ui-datepicker-div').hide();
    //            $('#calendar').fullCalendar(
    //                        'addResource',
    //                        { title: data.title },
    //                        true // scroll to the new resource?
    //            );
                //location.reload();
            }
            else{//Create error
                alert("Update error, please contact admin!")
            }
        },
        error: function(a,b,c){
//                console.log("Create error");
            alert("Update error, please contact admin!")
        }
    });
    var legendHtml = "";
    $.each(eventColors, function(key, value){
        var classAttr = "legend";
        if(isTodoItem(key)){
            classAttr += " todo"
        }
        legendHtml += '<div class="'+classAttr+'" style="background-color:'+value+'">'+key+'</div>';
    });
    $("#legendArea").html(legendHtml);
});

function redirectToUrl(target){
    $(window.location).attr('href', target);
}


function onDayClicked(date, jsEvent, view, resourceObj) {
    //alert('Clicked on: ' + date.format());

    //alert('Coordinates: ' + jsEvent.pageX + ',' + jsEvent.pageY);

    //alert('Current view: ' + view.name);

    // change the day's background color just for fun
    //$(this).css('background-color', 'red');

    $("#id_start").val(date.format("MM/DD/YYYY"));
    if(!isDialogSupported()){
        redirectToUrl('create_booking_req/?start='+date.format("MM/DD/YYYY")+'&resourceId='+resourceObj.id);
        return;
    }
    $( "#newBookingReqDialog" ).dialog("open");
    $("#id_end").datepicker( "option", "minDate", $("#id_start").datepicker( "getDate" ) );
    $("#id_end").focus();
    $("#id_resource").val(resourceObj.id);
}

var dateObjForGettingTimeZoneOffset = new Date();
var currentTimeZoneOffsetInHours = dateObjForGettingTimeZoneOffset.getTimezoneOffset() / 60;


function isAdminFor(event){
//    if((event.color=="red")//||(event.color=="blue")
//    ) return true;
    for(var index in gTodoLegend){
            if(event.color==eventColors[gTodoLegend[index]])
                return true
    }
    return false;
}


function onEventClick(calEvent, jsEvent, view) {

    //alert('Event: ' + calEvent.title);
    console.log(calEvent);

//    alert('Coordinates: ' + jsEvent.pageX + ',' + jsEvent.pageY);
//    alert('View: ' + view.name);
//
//    //change the border color just for fun
//    $(this).css('border-color', 'red');

    var targetEvent = $(this);
//    if(!isApprover()) return;
    if(!isAdminFor(calEvent)) return;

    if(!isDialogSupported()){
        redirectToUrl('req_update/'+calEvent.id +'/');
        return;
    }

    $("#bookingReqEditDialog").load('req_update_ajax/'+calEvent.id +'/', function(){
//        $( "#bookingReqEditDialog" ).dialog({"width": "800px"});
        $("#id_update-start").datepicker();
        $("#id_update-end").datepicker();

        $("#id_update-end").datepicker( "option", "minDate", $("#id_update-start").datepicker( "getDate" ) );

        $("#bookingReqEditForm").attr("action", 'req_update/'+calEvent.id +'/');
        $( "#bookingReqEditDialog" ).dialog("open");
    });


//
//    $( "#dialog-confirm" ).dialog( "option", "buttons",
//        [
//            {
//                text: "Approve",
//                click: function() {
//                    targetEvent.css('background-color', 'blue');
//                    $( this ).dialog( "close" );
//                          $.ajax({
//                                type: 'GET',
//                                url: "approve_request/",
//                                data: {"requestId": calEvent.id},
//                                success: function(a, b, c){
//                                    //console.log(a, b, c);
//                                    //console.log(a.result);
//                                    if(a.result=="true"){
//                                        targetEvent.css('background-color', approvedRequestColor);
//                                    }
//                                    else{
//                                        targetEvent.css('background-color', notApprovedRequestColor);
//                                    }
//                                }
//                            });
//                }
//            },
//            {
//                text: "Cancel",
//                click: function() {
//                    $( this ).dialog( "close" );
//                }
//            }
//         ]
//    );
//    $( "#dialog-confirm" ).dialog("open");

}