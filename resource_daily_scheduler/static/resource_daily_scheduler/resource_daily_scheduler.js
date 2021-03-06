function isDialogSupported(){
    //return false;
    var ieVer = msIeVersion();
//    if(ieVer && ieVer<9) return false;
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
//    return isAdmin;
    return false;
}

var gTodoLegend = ["Waiting for your approval", "Approved, you can change", "Ongoing", "Your request"
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
    $( "#newBookingReqDialog" ).dialog({"width": "800px", "autoOpen": false, title: "Create Request"});
    $( "#bookingReqEditDialog" ).dialog({"width": "800px", "autoOpen": false, title: "Approve/Update Request"});

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
        legendHtml += '<div class="'+classAttr+'" style="background-color:'+value[1]+
                        '" data-sort="'+value[0]+'">'+key+'</div>';
    });
    $("#legendArea").html(legendHtml);
    $('#legendArea div').sort(function (a, b) {

      var contentA =parseInt( $(a).attr('data-sort'));
      var contentB =parseInt( $(b).attr('data-sort'));
      return (contentA < contentB) ? -1 : (contentA > contentB) ? 1 : 0;
   }).appendTo( $("#legendArea") );

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

    openRequestDialog(date.format("MM/DD/YYYY"), resourceObj.id);
}

function openRequestDialog(formattedDate, resourceId){

    $("#id_start").val(formattedDate);
    if(!isDialogSupported()){
        redirectToUrl('create_booking_req/?start='+date.format("MM/DD/YYYY")+'&resourceId='+resourceId);
        return;
    }
    $( "#newBookingReqDialog" ).dialog("open");
    $("#id_end").datepicker( "option", "minDate", $("#id_start").datepicker( "getDate" ) );
    $("#id_end").focus();
    $("#id_resource").val(resourceId);
}

var dateObjForGettingTimeZoneOffset = new Date();
var currentTimeZoneOffsetInHours = dateObjForGettingTimeZoneOffset.getTimezoneOffset() / 60;


function isAdminFor(event){
    for(var index in gTodoLegend){
            if(event.color==eventColors[gTodoLegend[index]][1])
                return true
    }
    return false;
}


function isOwnerModification(calEvent){
    if(calEvent.color==eventColors["Your request"][1])
        return true;
    else
        return false;
}

function initRequestUpdateDialog(calEvent){
    $("#bookingReqEditDialog").load('req_update_ajax/'+calEvent.id +'/', function(){
        $("#id_update-start").datepicker();
        $("#id_update-end").datepicker();
        $("#id_update-end").datepicker( "option", "minDate", $("#id_update-start").datepicker( "getDate" ) );
        $("#bookingReqEditForm").attr("action", 'req_update/'+calEvent.id +'/');
        if(isOwnerModification(calEvent)){
            $("#id_update-is_approved").parents(".form-group").hide();
            $("#id_update-is_ongoing").parents(".form-group").hide();
            $("#id_update-is_completed").parents(".form-group").hide();
        }

        $("#id_update-is_canceled").parents(".form-group").hide();
        $("input[type=submit]", $("#bookingReqEditForm")).after('<button id="cancel">'+
            "Cancel Request</button>");
        $("#id_update-project").attr("autofocus", true);
        $("#cancel").click(function(){
            $("#id_update-is_canceled").prop('checked', true);
            $("#bookingReqEditForm").submit()
        });

        $( "#bookingReqEditDialog" ).dialog("open");
    });
}

function onEventClick(calEvent, jsEvent, view) {
//    var targetEvent = $(this);
//    if(!isApprover()) return;
    if(!isAdminFor(calEvent)) return;
    initRequestUpdateDialog(calEvent);
}