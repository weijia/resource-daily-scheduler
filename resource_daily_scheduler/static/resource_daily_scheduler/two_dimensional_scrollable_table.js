$(document).ready(function(){
  fnAdjustTable();
});

fnAdjustTable = function(){

  var colCount = $('#firstTr>td').length; //get total number of column

  var m = 0;
  var n = 0;
  var brow = 'mozilla';

  jQuery.each(jQuery.browser, function(i, val) {
    if(val == true){
      brow = i.toString();
    }
  });

  $('.tableHeader').each(function(i){
    if (m < colCount){

      if (brow == 'mozilla'){
        $('#firstTd').css("width",$('.tableFirstCol').innerWidth());//for adjusting first td
        $(this).css('width',$('.tableDiv td:eq('+m+')').innerWidth());//for assigning width to table Header div
      }
      else if (brow == 'msie'){
        $('#firstTd').css("width",$('.tableFirstCol').width());
        $(this).css('width',$('.tableDiv td:eq('+m+')').width()-2);//In IE there is difference of 2 px
      }
      else if (brow == 'safari'){
        $('#firstTd').css("width",$('.tableFirstCol').width());
        $(this).css('width',$('.tableDiv td:eq('+m+')').width());
      }
      else {
        $('#firstTd').css("width",$('.tableFirstCol').width());
        $(this).css('width',$('.tableDiv td:eq('+m+')').innerWidth());
      }
    }
    m++;
  });

  $('.tableFirstCol').each(function(i){
    if(brow == 'mozilla'){
      $(this).css('height',$('.tableDiv td:eq('+colCount*n+')').outerHeight());//for providing height using scrollable table column height
    }
    else if(brow == 'msie'){
      $(this).css('height',$('.tableDiv td:eq('+colCount*n+')').innerHeight()-2);
    }
    else {
      $(this).css('height',$('.tableDiv td:eq('+colCount*n+')').height());
    }
    n++;
  });

};

//function to support scrolling of title and first column
fnScroll = function(){
  $('.divHeader').scrollLeft($('.tableDiv').scrollLeft());
  $('.firstCol').scrollTop($('.tableDiv').scrollTop());
};
