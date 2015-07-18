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

//    extractDateFromDateStr: function(date){
//        //return date.split(" ")[0];
//        var momentDate = moment(date);
//        momentDate.subtract(1, 'seconds');
//        var dateStr = momentDate.format("YYYY-MM-DD");
////        var dateStr = moment.tz(date, "Asia/Shanghai").format("YYYY-MM-DD");
////        var dateStr = moment(date).tz("Asia/Shanghai").format("YYYY-MM-DD");
//        return dateStr;
//    },

    createBasicElement: function(){
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
    },

    isToday: function(value){
        return moment().format("YYYT-MM-DD") == moment(value).format("YYYT-MM-DD")
    },
 
    _create: function() {
//        var progress = this.options.value + "%";
//        this.element.addClass( "progressbar" ).text( progress );
//        console.log(this.options);
        var today = new Date();
        var startMonth = today.getMonth();
        //var year = start.getFullYear();
        this.start = new Date();
        this.start.setMonth(startMonth-2);
        //end.setYear(year+1);
        this.end = new Date();
        this.end.setMonth(startMonth+2);

        this.createBasicElement();

        var entries = [];
        var contentEntries = [];
        var borderColor = this.options.borderColor;
        var isWeekEnd = this.isWeekEnd;
        var thisValue = this;
//        var columnContainerTable = $(".columnContainerTable", this.element);
        $.each(this.getDays(this.start, this.end), function( index, value ) {
            var tdClasses=[];
            var tdContentClass = [];
            if(isWeekEnd(value)){
                tdClasses.push('weekend');
                tdContentClass.push('weekendInContent');
            }
            if(thisValue.isToday(value)){
                tdClasses.push("today");
                tdContentClass.push("today");
            }
            entries.push('<td class="'+tdClasses.join(" ")+'" date="'+thisValue.getFormattedDate(value)+'"><div>'+value.getDate()+"</div></td>");
            contentEntries.push('<td class="'+tdClasses.join(" ")+'"><div></div></td>');
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
        this.scrollToThisWeek();

        var startStr = moment(this.start).format("YYYY-MM-DD");
        var endStr = moment(this.end).format("YYYY-MM-DD");

        $.get(getSchedule+"?start="+startStr+"&end="+endStr+"&_="+Date.now, function(result){
            //$("div").html(result);
//            console.log(result);
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
    scrollToThisWeek: function(){
        var formattedDate = moment().subtract(7, "days").format("YYYY-MM-DD");
        var todayLeft = this.getDateLeftFromDateStr(formattedDate);
//        $('.divHeader').scrollLeft(todayLeft);
        $('.tableDiv').scrollLeft(todayLeft);
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
//    getDateLeft: function(eventStartDateStr){
//        var eventStartDate = this.extractDateFromDateStr(eventStartDateStr);
//        return this.getDateLeftFromDateStr(eventStartDate);
//    },
    getDateLeftFromMoment: function(momentDate){
        var momentStr = momentDate.format("YYYY-MM-DD");
        return this.getDateLeftFromDateStr(momentStr);
    },
    addEvent: function(event){
        var top = this.getResourceTop(event.resourceId);
        if(top!=null){
            var startMoment = moment(event.start);
            var endMoment = moment(event.end).subtract(1, "seconds");
            var tableStartMoment = moment(this.start);
            var tableEndMoment = moment(this.end);
            if(startMoment.diff(tableStartMoment)<0) startMoment = tableStartMoment;
            if(endMoment.diff(tableEndMoment)>0) endMoment = tableEndMoment;
            var left = this.getDateLeftFromMoment(startMoment);
            var width = this.getDateLeftFromMoment(endMoment) - left + 20;
            var additionalClass = "";
            if(event.className){
                additionalClass = " "+event.className;
            }
            var newElem = $('<div class="event'+additionalClass+'" style="top:'+top+'px;left:'+
            left+'px;width:'+width+'px;background-color:'+event.color+'" title="'+event.title+'">'+
            event.title+'</div>');
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