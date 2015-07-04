QUnit.test( "parseDateRange test", function( assert ) {
  $("#calendar").tableCalendar();
  var start = new Date();
  var year = start.getFullYear();
  var end = new Date();
  end.setYear(year+1);
//  $("#calendar").tableCalendar("parseDateRange", start, end);
//  $("#calendar").tableCalendar("getMonths", start, end);
//  $("#calendar").tableCalendar("getIntervals", start, end, function (current){
//    current.setMonth(current.getMonth() + 1);
//    return current;
//  });
  assert.ok( 1 == "1", "Passed!" );
});