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

    getFormattedDate: function(date){
//        return (data.getMonth() + 1) + "-" + data.getDate() + "-" + data.getFullYear()
        var month = date.getMonth() + 1;
        prefix = "";
        if(month < 10) prefix = "0";
        monthStr = prefix + month
        var day = date.getDate()
        prefix = "";
        if(day < 10) prefix = "0";
        dayStr = prefix + day

        return date.getFullYear() + "-" + monthStr + "-" + dayStr;
    },

    extractDateFromDateStr: function(date){
        return date.split(" ")[0];
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

        this.element.html(tableHeader//+tableBody+tableFooter
        );
        var entries = [];
        var contentEntries = [];
        var borderColor = this.options.borderColor;
        var isWeekEnd = this.isWeekEnd;
        var thisValue = this;
//        var columnContainerTable = $(".columnContainerTable", this.element);
        $.each(this.getDays(start, end), function( index, value ) {
            var tdClass="";
            var tdContentClass = "";
            if(isWeekEnd(value)){
                tdClass=' class="weekend"';
                tdContentClass=' class="weekendInContent"';
            }
            entries.push('<td'+tdClass+' date="'+thisValue.getFormattedDate(value)+'"><div>'+value.getDate()+"</div></td>");
            contentEntries.push('<td'+tdClass+'><div></div></td>');
        });
        $(".divHeader tr", this.element).html(entries.join(""));

        var tableElem = $(".firstCol table", this.element);
        var contentTable = $(".tableDiv table", this.element);
        $.each(this.options.resources, function( index, value ){
            tableElem.append('<tr><td resourceId="'+value.id+'" class="resourceName"><div>'+
                value.title+'</div></td><td><div class="rowContent"></div></td>'
            );
            contentTable.append("<tr>"+contentEntries.join("")+'</tr>');
        });

        $.each($(".firstCol td"), function(index, value){
            $(value).wrapInner('<a href="'+detailPath+$(value).attr('resourceId')+'/"></a>');
        });
        var formattedDate = this.getFormattedDate(new Date());
        var todayLeft = this.getDateLeftFromDateStr(formattedDate);
//        $('.divHeader').scrollLeft(todayLeft);
        $('.tableDiv').scrollLeft(todayLeft);


        $.get(getSchedule+"?start=2015-07-01&end=2015-08-01&_=1437058938623", function(result){
            //$("div").html(result);
            console.log(result);
            $.each($(result), function(index, value){
//                $(value).wrapInner('<a href="'+detailPath+$(value).attr('resourceId')+'/"></a>');
                thisValue.addEvent(value);
            });
        });
//        $(".event").click(function(a, b, c){
//            console.log(a, b, c);
//            onEventClick();
//        });
        $(".tableDiv").on("click", ".event", function(event){
//            console.log(a, b, c);
            var event = $(event.currentTarget).data("event");
            onEventClick(event);
        });

        $(".dataTable").on("click", "td", function(event){
//            console.log(a, b, c);
            var cellIndex = $(event.currentTarget).index();
            var rowIndex = $(event.currentTarget).parent().index();
            var resourceTd = $("td", $(".firstCol tr")[rowIndex]);
            var resourceId = $(resourceTd).attr("resourceId");
            var dateCell = $(".headerTable td")[cellIndex]
            var dateStr = $(dateCell).attr("date");
            var date = moment(dateStr);
//            dateStr.replace("-", "/");
//            var date = new Date(dateStr);
            var formattedDate = date.format("MM/DD/YYYY")
            openRequestDialog(formattedDate, resourceId);
        });


    },
    getResourceTop: function(resourceId){
        var selectorStr = ".resourceName[resourceId="+resourceId+"]";
        var elem = $(selectorStr);
        if(elem.length){
            var top = elem.offset().top - elem.parent().parent().offset().top;
            return top;
        }
        return null;
    },
    getDateLeftFromDateStr: function(eventStartDate){
        var eventDateTd = $(".headerTable td[date="+eventStartDate+"]");
        var left = eventDateTd.offset().left - eventDateTd.parent().parent().offset().left;
        return left;    
    },
    getDateLeft: function(eventStartDateStr){
        var eventStartDate = this.extractDateFromDateStr(eventStartDateStr);
        return this.getDateLeftFromDateStr(eventStartDate);
    },
    addEvent: function(event){
        var top = this.getResourceTop(event.resourceId);
        if(top!=null){
            var left = this.getDateLeft(event.start);
            var width = this.getDateLeft(event.end) - left + 20;
            var newElem = $('<div class="event" style="top:'+top+'px;left:'+
            left+'px;width:'+width+'px;background-color:'+event.color+'">'+'</div>');
            $(".tableDiv").append(newElem);
            newElem.data("event", event);
        }
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