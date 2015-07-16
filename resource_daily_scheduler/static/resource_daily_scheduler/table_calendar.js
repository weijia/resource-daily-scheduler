$.widget( "resourceScheduler.tableCalendar", {

    options: {
        borderColor: "#DDD"
    },
    isWeekEnd: function(date){
        var weekday = date.getDay();
        if(weekday==0||weekday==6){
            return true;
        }
        else{
            return false;
        }
    },
 
    _create: function() {
//        var progress = this.options.value + "%";
//        this.element.addClass( "progressbar" ).text( progress );
//        console.log(this.options);
        var today = new Date();
        var startMonth = today.getMonth();
        //var year = start.getFullYear();
        var start = new Date();
        start.setMonth(startMonth-2);
        //end.setYear(year+1);
        var end = new Date();
        end.setMonth(startMonth+2);
        // TODO: use a separate table for rows, so we will not get the limitation
        // TODO: on the height setting of the table. Check fullcalendar.
        var tableHeader = '<div class="fc-toolbar"><div class="fc-left"></div></div>'+
                            '<div>'+
                                '<div class="topTableDiv">'+
                                    '<table class="topTable">'+
                                        '<tr>' +
                                            '<td class="firstTd">' +
                                            '</td>' +
                                            '<td>' +
                                                '<div class="divHeader">' +
                                                    '<table class="headerTable">' +
                                                    '<tr><!--<td></td>--></tr>' +
                                                    '</table>' +
                                                '</div>' +
                                            '</td>' +
                                        '</tr>' +
                                        '<tr>' +
                                            '<td valign="top">' +
                                                '<div class="firstCol">' +
                                                    '<table>' +
//                                                        '<tr><td></td></tr>' +
                                                    '</table>' +
                                                '<div>' +
                                            '</td>' +
                                            '<td valign="top">' +
                                                '<div class="tableDiv" onscroll="fnScroll()" >' +
                                                    '<table class="dataTable">' +
//                                                        '<tr id="firstTr">' +
//                                                            '<td></td>' +
//                                                        '</tr>' +
                                                    '</table>' +
                                                '</div>' +
                                            '</td>' +
                                        '</tr>' +
                                    '</table>'+
                                '</div>' +
                            '</div>'


//                            +'<div class="calendarViewPort">'+
//                            '<div><table class="calendar"'+
//                            '><thead><tr></tr></thead>';
//        var tableBody = '';
////        for(var index=0; index<this.options.resources.length; index++){
////            tableBody += '<tr class="content"></tr>';
////        }
//        var tableFooter = '';//'<tr class="lastLine"></tr>'+
//                            //'</table></div></div>';
////        var tableElem = this.element;
////        tableElem.html(tableHeader+tableBody+tableFooter);
        this.element.html(tableHeader//+tableBody+tableFooter
        );
        var entries = [];
        var contentEntries = [];
        var borderColor = this.options.borderColor;
        var isWeekEnd = this.isWeekEnd;
//        var columnContainerTable = $(".columnContainerTable", this.element);
        $.each(this.getDays(start, end), function( index, value ) {
            var tdClass="";
            var tdContentClass = "";
            if(isWeekEnd(value)){
                tdClass=' class="weekend"';
                tdContentClass=' class="weekendInContent"';
            }
//            columnContainerTable.append('<td'+tdClass+'><div>'+value.getDate()+"</div></td>");
            entries.push('<td'+tdClass+'><div>'+value.getDate()+"</div></td>");
//            contentEntries.push('<td'+tdContentClass+'><div></div></td>');
            contentEntries.push('<td><div></div></td>');
        });
        $(".divHeader tr", this.element).html(entries.join(""));
//        $(".columnContainerContent", columnContainerTable).html(contentEntries.join(""));
//        $("thead > tr", this.element).html('<td><div class="resourceNameHeader">Item title</div></td>'
//            //`+entries.join("")
//        );
        var tableElem = $(".firstCol table", this.element);
        var contentTable = $(".tableDiv table", this.element);
        $.each(this.options.resources, function( index, value ){
            tableElem.append('<tr><td resourceId="'+value.id+'" class="resourceName"><div>'+
                value.title+'</div></td><td><div class="rowContent"></div></td>'
            //+ contentEntries.join("")+'</tr>'
            );
            contentTable.append("<tr>"+contentEntries.join("")+'</tr>');
        });

        $.each($(".firstCol td"), function(index, value){
            $(value).wrapInner('<a href="'+detailPath+$(value).attr('resourceId')+'/"></a>');
        });

        $.get(getSchedule+"?start=2015-07-01&end=2015-08-01&_=1437058938623", function(result){
            //$("div").html(result);
            console.log(result);
        });


////        $("tr.lastLine", this.element).html('<td><div></div></td>'+contentEntries.join(""));
//        tableElem.append('<tr><td class="resourceName"></td><td></td>');
    },
    // Return an array of Date objects between `from` and `to`
    getDays: function (from, to) {
        return this.getIntervals(from, to, function(current){
            current.setDate(current.getDate() + 1);
            return current;
        })
    },
    getMonths: function (from, to){
        return this.getIntervals(from, to, function(current){
            current.setMonth(current.getMonth() + 1);
            return current;
        })
    },
    getIntervals: function(from, to, nextIntervalCallback){
        var current = new Date(from.getTime());
        var end = new Date(to.getTime()); // <- never used?
        var ret = [];
        var i = 0;
        do {
            ret[i++] = new Date(current.getTime());
            current = nextIntervalCallback(current);
        } while (current.getTime() <= to.getTime());
        return ret;
    }
});