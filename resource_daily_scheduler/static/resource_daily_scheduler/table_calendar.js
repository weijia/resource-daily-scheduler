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
        var start = new Date();
        var year = start.getFullYear();
        var end = new Date();
        end.setYear(year+1);
        this.element.html('<div class="calendarViewPort">'+
        '<div><table class="calendar"'+
        '><thead><tr></tr></thead><tr class="content"></tr>'+
        '<tr class="content"></tr></table></div></div>');
        var entries = [];
        var contentEntries = [];
        var borderColor = this.options.borderColor;
        var isWeekEnd = this.isWeekEnd;
        $.each(this.getDays(start, end), function( index, value ) {
            var tdClass="";
            if(isWeekEnd(value)){
                tdClass=' class="weekend"';
            }
            entries.push('<td'+tdClass+'><div>'+value.getDate()+"</div></td>");
            contentEntries.push('<td><div></div></td>');
        });
        $("thead > tr", this.element).html('<td>Item title</td>'+entries.join(""));
        $("tr.content", this.element).html('<td></td>'+contentEntries.join(""));
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